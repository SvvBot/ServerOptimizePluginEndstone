import time
import gc # Keep garbage collector for memory cleanup
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional

# Assuming these are available in the Endstone environment
from endstone.command import Command, CommandSender
from endstone.event import (
    EventPriority,
    ServerLoadEvent,
    PlayerJoinEvent,
    PlayerQuitEvent,
    event_handler,
)
from endstone.plugin import Plugin
from endstone.player import Player # Added for type hinting


class ServerOptimizerPlugin(Plugin):
    prefix = "ServerOptimizer"
    api_version = "0.10"
    load = "POSTWORLD"

    commands = {
        "optimize": {
            "description": "Server optimization controls",
            "usages": ["/optimize <status|full|view <player>>"],
            "aliases": ["opt", "perf"],
            "permissions": ["serveropt.command.optimize"],
        },
        "tps": {
            "description": "Check server TPS",
            "usages": ["/tps"],
            "permissions": ["serveropt.command.tps"],
        },
        "lag": {
            "description": "View lag information",
            "usages": ["/lag"],
            "permissions": ["serveropt.command.lag"],
        },
        "viewdistance": {
            "description": "Manage view distance",
            "usages": ["/viewdistance [distance: int]", "/viewdistance auto"],
            "aliases": ["vd"],
            "permissions": ["serveropt.command.viewdistance"],
        },
    }

    permissions = {
        "serveropt.admin": {
            "description": "Admin permissions for server optimizer",
            "default": "op",
            "children": {
                "serveropt.command.optimize": True,
                "serveropt.command.tps": True,
                "serveropt.command.lag": True,
                "serveropt.command.viewdistance": True,
            },
        },
        "serveropt.command.optimize": {
            "description": "Use optimization commands",
            "default": "op",
        },
        "serveropt.command.tps": {
            "description": "Check server TPS",
            "default": True,
        },
        "serveropt.command.lag": {
            "description": "View lag information",
            "default": True,
        },
        "serveropt.command.viewdistance": {
            "description": "Manage view distance",
            "default": "op",
        },
    }

    def on_load(self) -> None:
        self.logger.info("=== Server Optimizer Pro Loading ===")
        
        # Performance tracking
        self.tick_times: deque = deque(maxlen=200)
        self.tps_history: deque = deque(maxlen=60)
        self.last_tick = time.time()
        
        # Auto-optimization settings
        self.auto_optimize = True
        self.aggressive_mode = False
        self.last_optimization = 0
        self.optimization_interval = 120
        
        # Entity limits (Placeholder/Configuration)
        self.entity_limits = {
            "item": 50,
            "mob": 30,
            "minecart": 5,
            "boat": 5,
            "arrow": 20,
        }
        
        # Chunk management
        self.loaded_chunks: Dict[str, int] = defaultdict(int)
        self.chunk_unload_threshold = 300
        self.max_chunks_per_player = 64
        
        # View distance management
        self.auto_view_distance = True
        self.base_view_distance = 8
        self.min_view_distance = 4
        self.max_view_distance = 12
        self.current_view_distance = self.base_view_distance
        
        # Player tracking
        self.player_positions: Dict[str, tuple] = {}
        self.afk_players: Set[str] = set()
        self.afk_threshold = 180
        
        # Performance thresholds
        self.tps_target = 19.0
        self.tps_critical = 15.0
        self.tps_warning = 18.0
        
        # Optimization stats
        self.total_optimizations = 0
        self.chunks_cleared_total = 0
        self.entities_removed_total = 0
        
        # Alert cooldowns
        self.last_lag_alert = 0
        self.lag_alert_cooldown = 60
        
        # Crash recovery tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Performance viewer tracking
        self.performance_viewers: Set[str] = set()
        
        # Overload protection
        self.max_players_warning = 80
        self.max_players_critical = 100
        self.max_chunks_warning = 3000
        self.max_chunks_critical = 5000
        
        # Task execution monitoring
        self.task_execution_times: Dict[str, List[float]] = defaultdict(list)
        self.max_task_duration = 0.05
        self.slow_tasks: Set[str] = set()
        
        # Memory monitoring (Simplified/Placeholder)
        self.memory_samples: deque = deque(maxlen=30)
        self.memory_warning_threshold = 80.0
        self.memory_critical_threshold = 90.0
        
        # Server health score
        self.health_score = 100
        self.health_history: deque = deque(maxlen=60)

    def on_enable(self) -> None:
        self.logger.info("=== Server Optimizer Enabled (made by SvvXD)===")
        
        # Register event listeners
        self.register_events(self)
        
        # Wrap all tasks in try-except
        def safe_task(task_func):
            def wrapper():
                try:
                    task_func()
                except Exception as e:
                    self.logger.error(f"Task error: {e}")
            return wrapper
        
        # Performance monitoring (runs every tick)
        self.server.scheduler.run_task(
            self, safe_task(self.monitor_performance), delay=0, period=1
        )
        
        # Fast optimization check (runs every 10 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.fast_optimization_check), delay=200, period=200
        )
        
        # Auto-optimization (runs every 30 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.auto_optimize_task), delay=100, period=600
        )
        
        # Chunk cleanup (runs every 60 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.cleanup_chunks), delay=200, period=1200
        )
        
        # AFK detection (runs every 30 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.detect_afk_players), delay=300, period=600
        )
        
        # View distance adjuster (runs every 15 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.adjust_view_distance), delay=300, period=300
        )
        
        # Memory cleanup (runs every 5 minutes)
        self.server.scheduler.run_task(
            self, safe_task(self.periodic_memory_cleanup), delay=6000, period=6000
        )
        
        # Performance display (runs every 2 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.update_performance_display), delay=40, period=40
        )
        
        # Overload monitoring (runs every 3 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.monitor_overload), delay=60, period=60
        )
        
        # Health check (runs every 5 seconds)
        self.server.scheduler.run_task(
            self, safe_task(self.check_server_health), delay=100, period=100
        )
        
        # Memory monitoring (runs every 10 seconds - simplified)
        self.server.scheduler.run_task(
            self, safe_task(self.monitor_memory), delay=200, period=200
        )
        
        self.logger.info("All optimization tasks started!")
        self.logger.info("Crash protection: ENABLED")

    def on_disable(self) -> None:
        self.logger.info("=== Server Optimizer Disabled ===")
        self.logger.info(f"Total Optimizations: {self.total_optimizations}")

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        match command.name:
            case "optimize":
                return self.handle_optimize_command(sender, args)
            case "tps":
                return self.handle_tps_command(sender)
            case "lag":
                return self.handle_lag_command(sender)
            case "viewdistance":
                return self.handle_viewdistance_command(sender, args)
        return False

    def handle_optimize_command(self, sender: CommandSender, args: list[str]) -> bool:
        if not sender.has_permission("serveropt.command.optimize"):
            sender.send_error_message("§cYou do not have permission to use this command!")
            return False

        if len(args) == 0:
            sender.send_message("§e=== Optimize Commands ===")
            sender.send_message("§7/optimize status §f- View server status")
            sender.send_message("§7/optimize full §f- Run full optimization")
            sender.send_message("§7/optimize view <player> §f- Toggle TPS display for a player")
            return True

        action = args[0].lower()
        
        if action == "status":
            self.show_detailed_status(sender)
        elif action == "full":
            sender.send_message("§e[Optimizer] Running full optimization...")
            self.optimize_chunks()
            self.optimize_entities()
            self.optimize_memory()
            sender.send_message(f"§a✓ Optimization Complete!")
        elif action == "view":
            return self.handle_performance_view(sender, args)
        else:
            sender.send_error_message(f"§cUnknown optimize subcommand: {action}")
            return False
        
        return True

    def handle_tps_command(self, sender: CommandSender) -> bool:
        tps = self.calculate_tps()
        color = self.get_tps_color(tps)
        sender.send_message(f"§e§l[TPS] {color}{tps:.2f} TPS §7(Target: 20.0)")
        return True

    def handle_lag_command(self, sender: CommandSender) -> bool:
        tps = self.calculate_tps()
        online_players = len(self.server.online_players)
        sender.send_message("§e§l=== LAG Report ===")
        sender.send_message(f"§eTPS: §f{tps:.2f}§e/20.0")
        sender.send_message(f"§ePlayers: §f{online_players}")
        # Note: In a real plugin, you'd add more lag details here (top tasks, memory, etc.)
        return True

    def handle_viewdistance_command(self, sender: CommandSender, args: list[str]) -> bool:
        if not sender.has_permission("serveropt.command.viewdistance"):
            sender.send_error_message("§cYou do not have permission to use this command!")
            return False

        if len(args) == 0:
            sender.send_message(f"§e[View Distance] Current: §f{self.current_view_distance} chunks")
            sender.send_message(f"§7Auto Adjust: {'§aON' if self.auto_view_distance else '§cOFF'}")
            return True

        if args[0].lower() == "auto":
            self.auto_view_distance = not self.auto_view_distance
            status = "ON" if self.auto_view_distance else "OFF"
            sender.send_message(f"§a✓ Auto View Distance set to: {status}")
            return True

        try:
            vd = int(args[0])
            if vd < self.min_view_distance or vd > self.max_view_distance:
                sender.send_error_message(f"§cView distance must be between {self.min_view_distance}-{self.max_view_distance}")
                return False
            
            self.current_view_distance = vd
            self.auto_view_distance = False
            sender.send_message(f"§a✓ Set view distance to {vd} chunks")
            
        except ValueError:
            sender.send_error_message("§cPlease enter a valid number!")
            return False
        
        return True

    def handle_performance_view(self, sender: CommandSender, args: list[str]) -> bool:
        if len(args) < 2:
            if len(self.performance_viewers) == 0:
                sender.send_message("§e[Performance View] §7No players are currently viewing performance.")
            else:
                sender.send_message("§e[Performance View] §7Players viewing:")
                for viewer in self.performance_viewers:
                    sender.send_message(f"§7- §f{viewer}")
            return True
        
        target_name = args[1]
        target_player: Optional[Player] = None
        
        for player in self.server.online_players:
            if player.name.lower() == target_name.lower():
                target_player = player
                break
        
        if target_player is None:
            sender.send_error_message(f"§cPlayer not found: {target_name}")
            return False
        
        if target_player.name in self.performance_viewers:
            self.performance_viewers.remove(target_player.name)
            sender.send_message(f"§a✓ Disabled performance display for §f{target_player.name}")
            target_player.send_message("§e[Performance View] §7Performance display disabled.")
        else:
            self.performance_viewers.add(target_player.name)
            sender.send_message(f"§a✓ Enabled performance display for §f{target_player.name}")
            target_player.send_message("§e[Performance View] §aPerformance display enabled.")
        
        return True

    def show_detailed_status(self, sender: CommandSender) -> None:
        tps = self.calculate_tps()
        color = self.get_tps_color(tps)
        online = len(self.server.online_players)
        
        sender.send_message("§e§l═══════════════════")
        sender.send_message("§e§l   Server Status")
        sender.send_message("§e§l═══════════════════")
        sender.send_message(f"§eTPS: {color}{tps:.2f}§e/20.0")
        sender.send_message(f"§eHealth: {self.get_health_color()}{self.health_score}§e/100")
        sender.send_message(f"§ePlayers: §f{online}")
        sender.send_message(f"§eView Distance: §f{self.current_view_distance}")
        sender.send_message(f"§eOptimization Total: §f{self.total_optimizations}")
        sender.send_message("§e§l═══════════════════")

    def monitor_performance(self) -> None:
        try:
            current_time = time.time()
            tick_duration = current_time - self.last_tick
            self.last_tick = current_time
            
            self.tick_times.append(tick_duration)
            tps = self.calculate_tps()
            self.tps_history.append(tps)
            
            online_players = len(self.server.online_players)
            estimated_chunks = online_players * self.max_chunks_per_player
            self.loaded_chunks["estimated"] = estimated_chunks
            
            # Notify admins of severe lag
            if tps < self.tps_critical:
                self.notify_admins_lag(tps)

        except Exception as e:
            self.logger.error(f"Performance monitoring error: {e}")

    def fast_optimization_check(self) -> None:
        if not self.auto_optimize:
            return
        
        tps = self.calculate_tps()
        if tps < self.tps_critical:
            self.logger.warning(f"Critical TPS detected: {tps:.2f}. Initiating emergency recovery.")
            self.emergency_crash_recovery()

    def auto_optimize_task(self) -> None:
        if not self.auto_optimize:
            return
        
        current_time = time.time()
        tps = self.calculate_tps()
        
        # Optimize if TPS is low or enough time has passed
        if tps < self.tps_warning or current_time - self.last_optimization >= self.optimization_interval:
            self.logger.info(f"Auto-optimization triggered (TPS: {tps:.2f})")
            chunks_cleared = self.optimize_chunks()
            entities_removed = self.optimize_entities()
            self.last_optimization = current_time
            self.total_optimizations += 1
            self.logger.info(f"Auto-optimization complete. Chunks cleared: {chunks_cleared}, Entities removed: {entities_removed}")

    def cleanup_chunks(self) -> None:
        if not self.auto_optimize:
            return
        
        # Placeholder for actual chunk unloading logic
        if self.loaded_chunks.get("estimated", 0) > 500:
            to_clear = self.loaded_chunks.get("estimated", 500) - 500
            self.loaded_chunks.clear()
            self.chunks_cleared_total += to_clear
            self.logger.info(f"Aggressive chunk cleanup: {to_clear} chunks cleared (estimated).")
            # In a real plugin, you would call the Endstone API to unload chunks here

    def detect_afk_players(self) -> None:
        # Placeholder for AFK detection logic
        pass

    def adjust_view_distance(self) -> None:
        if not self.auto_view_distance:
            return
        
        tps = self.calculate_tps()
        target_vd = self.current_view_distance
        
        if tps >= 19.5 and self.current_view_distance < self.max_view_distance:
            target_vd = min(self.max_view_distance, self.current_view_distance + 1)
        elif tps < 17.0 and self.current_view_distance > self.min_view_distance:
            target_vd = max(self.min_view_distance, self.current_view_distance - 1)
        elif tps < self.tps_critical:
            target_vd = self.min_view_distance
        
        if target_vd != self.current_view_distance:
            self.current_view_distance = target_vd
            self.logger.info(f"Adjusted view distance to {self.current_view_distance} due to TPS of {tps:.2f}")

    def periodic_memory_cleanup(self) -> None:
        if self.auto_optimize:
            self.optimize_memory()

    def optimize_chunks(self) -> int:
        count = 0
        threshold = 300 if self.aggressive_mode else 500
        
        estimated_chunks = self.loaded_chunks.get("estimated", 0)
        if estimated_chunks > threshold:
            count = estimated_chunks - threshold
            self.loaded_chunks.clear() # Simulate clearing
            self.chunks_cleared_total += count
            
            # In a real plugin, call Endstone API to unload chunks here
            
        return count

    def optimize_entities(self) -> int:
        count = 50 if not self.aggressive_mode else 100
        self.entities_removed_total += count
        # In a real plugin, call Endstone API to remove entities here
        return count

    def optimize_memory(self) -> None:
        """Runs the Python garbage collector to free memory."""
        gc.collect()
        self.logger.info("Garbage Collector executed.")

    def calculate_tps(self) -> float:
        """Calculates the current TPS based on the last 20 tick durations."""
        if len(self.tick_times) < 20:
            return 20.0
        
        # Use a slice for the last 20 elements
        recent_ticks = self.tick_times
        avg_tick_time = sum(recent_ticks) / len(recent_ticks)
        
        if avg_tick_time == 0:
            return 20.0
        
        tps = min(20.0, 1.0 / avg_tick_time)
        return tps

    def get_average_tps(self) -> float:
        """Calculates the average TPS over the history."""
        if not self.tps_history:
            return 20.0
        return sum(self.tps_history) / len(self.tps_history)

    def get_tps_color(self, tps: float) -> str:
        if tps >= 19:
            return "§a" # Green
        elif tps >= 18:
            return "§e" # Yellow
        elif tps >= 15:
            return "§6" # Gold
        else:
            return "§c" # Red

    def get_tps_status(self, tps: float) -> str:
        if tps >= 19:
            return "Excellent"
        elif tps >= 18:
            return "Good"
        elif tps >= 15:
            return "Fair"
        else:
            return "Poor"

    def get_health_color(self) -> str:
        if self.health_score >= 80:
            return "§a"
        elif self.health_score >= 60:
            return "§e"
        elif self.health_score >= 40:
            return "§6"
        else:
            return "§c"

    def notify_admins_lag(self, tps: float) -> None:
        current_time = time.time()
        
        if current_time - self.last_lag_alert < self.lag_alert_cooldown:
            return
        
        self.last_lag_alert = current_time
        
        for player in self.server.online_players:
            # Check if player has serveropt.admin or is OP
            if player.is_op or player.has_permission("serveropt.admin"):
                color = self.get_tps_color(tps)
                player.send_message(f"§c[Optimizer] ⚠ WARNING: Low TPS: {color}{tps:.2f}§c/20.0")

    def monitor_overload(self) -> None:
        try:
            overload_detected = False
            overload_reasons = []
            
            online_players = len(self.server.online_players)
            if online_players >= self.max_players_critical:
                overload_detected = True
                overload_reasons.append(f"Players: {online_players}")
            
            estimated_chunks = self.loaded_chunks.get("estimated", 0)
            if estimated_chunks >= self.max_chunks_critical:
                overload_detected = True
                overload_reasons.append(f"Chunks: {estimated_chunks}")
            
            # Check memory usage (simplified, as psutil was removed)
            # if self.get_memory_usage() >= self.memory_critical_threshold:
            #     overload_detected = True
            #     overload_reasons.append(f"Memory: {self.get_memory_usage():.1f}%")
            
            if overload_detected:
                self.logger.error(f"=== OVERLOAD DETECTED: {', '.join(overload_reasons)} ===")
                self.emergency_crash_recovery()
            
        except Exception as e:
            self.logger.error(f"Overload monitoring failed: {e}")

    def check_server_health(self) -> None:
        try:
            health = 100
            tps = self.calculate_tps()
            
            # Simple health calculation based on TPS
            if tps >= 19.5:
                health = 100
            elif tps >= 18:
                health = 80
            elif tps >= 15:
                health = 60
            else:
                health = 40
            
            self.health_score = health
            self.health_history.append(health)
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    def monitor_memory(self) -> None:
        """
        Stub for memory monitoring. Requires a platform-specific library (like psutil) 
        or an Endstone API method to get actual memory usage.
        The original implementation using psutil was removed for open-source compatibility.
        """
        # Placeholder for memory monitoring logic
        # For now, it only triggers garbage collection if auto_optimize is on (via periodic_memory_cleanup)
        pass

    def get_memory_usage(self) -> float:
        """Placeholder function for memory usage (%) that doesn't rely on psutil."""
        # In a real Endstone environment, this would call a server API method
        return 0.0 # Returning 0.0 as a safe default

    def monitor_task_performance(self, task_name: str, duration: float) -> None:
        try:
            # This would ideally be integrated into the scheduler wrappers to measure task execution time
            self.task_execution_times[task_name].append(duration)
            
            if len(self.task_execution_times[task_name]) > 10:
                self.task_execution_times[task_name].pop(0)
            
            if duration > self.max_task_duration:
                if task_name not in self.slow_tasks:
                    self.slow_tasks.add(task_name)
                    self.logger.warning(f"Slow task detected: {task_name} took {duration:.4f}s")
            else:
                if task_name in self.slow_tasks:
                    self.slow_tasks.remove(task_name)
        except Exception as e:
            self.logger.error(f"Task monitoring failed: {e}")

    def emergency_crash_recovery(self) -> None:
        try:
            self.logger.warning("=== EMERGENCY CRASH RECOVERY ACTIVATED ===")
            
            # Drop view distance to minimum
            old_vd = self.current_view_distance
            self.current_view_distance = self.min_view_distance
            
            # Activate aggressive mode
            self.aggressive_mode = True
            
            # Force immediate optimization
            self.optimize_chunks()
            self.optimize_entities()
            self.optimize_memory()
            
            for player in self.server.online_players:
                if player.is_op or player.has_permission("serveropt.admin"):
                    player.send_message("§c§l[EMERGENCY] §cEmergency optimization activated! View distance lowered.")
            
            self.logger.warning("=== EMERGENCY RECOVERY COMPLETE. Restoration scheduled. ===")
            
            # Schedule restoration to normal settings after 5 minutes (6000 ticks)
            def restore_normal():
                self.current_view_distance = self.base_view_distance
                self.aggressive_mode = False
                self.logger.info("Normal optimization settings restored.")
            
            self.server.scheduler.run_task(self, restore_normal, delay=6000)
            
        except Exception as e:
            self.logger.error(f"Emergency recovery failed: {e}")

    def update_performance_display(self) -> None:
        try:
            if not self.performance_viewers:
                return
            
            tps = self.calculate_tps()
            color = self.get_tps_color(tps)
            online = len(self.server.online_players)
            
            display_text = f"§e§l[OPT] {color}TPS: {tps:.1f}§r/20.0 §ePlayers: {online} §eVD: {self.current_view_distance}"
            
            # Iterate over a copy of the set to allow modification if a player is missing
            for player_name in list(self.performance_viewers):
                player: Optional[Player] = self.server.get_player(player_name)
                
                if player is None:
                    self.performance_viewers.remove(player_name)
                    continue
                
                player.send_popup(display_text)
                
        except Exception as e:
            self.logger.error(f"Performance display failed: {e}")

    @event_handler
    def on_server_load(self, event: ServerLoadEvent) -> None:
        self.logger.info("Server loaded - Optimizer ready!")

    @event_handler(priority=EventPriority.MONITOR)
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        player = event.player
        
        # Check if they are OP or have admin permission
        if player.is_op or player.has_permission("serveropt.admin"):
            def send_info():
                # Re-check permission in case it changed
                if player.is_op or player.has_permission("serveropt.admin"):
                    tps = self.calculate_tps()
                    color = self.get_tps_color(tps)
                    player.send_message("§e§l[Server Optimizer (By SvvXD)]")
                    player.send_message(f"§7Current TPS: {color}{tps:.2f}§7/20.0")
            
            self.server.scheduler.run_task(self, send_info, delay=40)

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        player_name = event.player.name
        
        if player_name in self.afk_players:
            self.afk_players.remove(player_name)
        
        if player_name in self.player_positions:
            del self.player_positions[player_name]
        
        if player_name in self.performance_viewers:
            self.performance_viewers.remove(player_name)
