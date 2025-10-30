-----

# ServerOptimizerPlugin (for Endstone/Bedrock) 🚀

## ⚡ Overview

**ServerOptimizer** is a high-performance plugin specifically designed for **Endstone** servers (Minecraft Bedrock Edition) to monitor performance in real-time and automatically implement critical optimization routines to maintain a solid **20.0 TPS** (Ticks Per Second).

Featuring dynamic view distance adjustment, emergency crash recovery, and detailed performance reporting, this plugin is an essential tool for stabilizing and scaling your server.

### ✨ Key Features

  * **Real-time TPS Monitoring:** Accurately tracks and records TPS values every second.
  * **Dynamic View Distance:** Automatically adjusts the server's view distance based on live TPS to prevent lag spikes.
  * **Emergency Crash Recovery:** Drastically reduces settings and runs aggressive cleanup when critical lag is detected (`TPS < 15.0`).
  * **Automatic Cleanup:** Periodically performs memory management (Garbage Collection) and clears estimated unnecessary chunks and entities.
  * **Performance Display:** Allows administrators to toggle a real-time TPS and player count popup display for specific players.

-----

## ⚙️ Installation

### Prerequisites

  * An active **Endstone** server instance (version `0.10` or higher).
  * **Python 3.8+** for running the plugin and for developers wishing to build from source.

### Option 1: Install the Pre-Built Plugin (Recommended)

1.  **Download:** Download the latest release of the `ServerOptimizerPlugin.py` file.
2.  **Upload:** Place the file into your server's `plugins/` directory.
3.  **Restart/Reload:** Restart your Endstone server or use the command `/reload` to load the plugin.

### Option 2: Building from Source (For Developers)

To ensure a clean and isolated build environment, use **pipx** to manage the build dependencies.

1.  **Install `pipx`:** If you don't have it, install the tool that runs Python applications in isolated environments.

    ```bash
    pip install pipx
    ```

2.  **Clone or Download:** Obtain the source code for the plugin.

3.  **Build the Package:** Use `pipx` to run the `build` module, which will create the final distributable package (often a `.whl` or the source file itself).

    ```bash
    # This command uses pipx to run the 'build' tool to create the package
    pipx run build --wheel
    ```

4.  **Deploy:** Place the resulting plugin file (`ServerOptimizerPlugin.py` or the built package contents) into your server's `plugins/` directory.

-----

## 📚 Commands and Permissions

| Command | Usage | Description | Permission | Default |
| :--- | :--- | :--- | :--- | :--- |
| **`/tps`** | `/tps` | Check the current server TPS (Ticks Per Second). | `serveropt.command.tps` | True (All players) |
| **`/lag`** | `/lag` | View a simple lag/status report. | `serveropt.command.lag` | True (All players) |
| **`/optimize`** | `/optimize status` | View the detailed performance status (TPS, Health, View Distance). | `serveropt.command.optimize` | OP |
| | `/optimize full` | Manually run a full optimization (Chunk/Entity/Memory cleanup). | `serveropt.command.optimize` | OP |
| | `/optimize view <player>` | Toggle the continuous performance display for a player. | `serveropt.command.optimize` | OP |
| **`/viewdistance`** | `/vd [distance]` | Manually set the server's view distance (between `4` and `12`). | `serveropt.command.viewdistance` | OP |
| | `/vd auto` | Toggle the **Dynamic View Distance** feature (enabled by default). | `serveropt.command.viewdistance` | OP |

### Administrator Permission Node

The permission node `serveropt.admin` grants access to all administrative commands (`/optimize` and `/viewdistance`). This is automatically granted to OP players.

-----

## 🔧 Configuration

Since this is a single-file Python plugin, configuration is managed by editing the variables directly within the `on_load` method of the `ServerOptimizerPlugin.py` file.

Key variables you may wish to adjust in the `on_load` method:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `self.auto_optimize` | `True` | Master switch for all scheduled optimization routines. |
| `self.optimization_interval` | `120` | How often (in seconds) the full auto-optimization runs, regardless of TPS. |
| `self.base_view_distance` | `8` | The standard view distance for auto-adjustment. |
| `self.min_view_distance` | `4` | The lowest view distance the plugin will set during lag. |
| `self.max_view_distance` | `12` | The highest view distance the plugin will set when TPS is high. |
| `self.tps_critical` | `15.0` | TPS level that triggers the **Emergency Crash Recovery**. |
| `self.tps_warning` | `18.0` | TPS level that triggers the scheduled **Auto-Optimization** run. |

-----

## 📝 Extending and Contributing

This plugin is designed to be easily extensible. If you wish to contribute to its development:

1.  **Fork** the repository.
2.  **Implement** new optimization routines (e.g., specific entity cleanup using Endstone API calls).
3.  **Submit** a Pull Request detailing your changes.

**Note:** The plugin maintains high compatibility by avoiding reliance on non-standard external Python libraries (like `psutil`). All core functionality relies on the standard Python library and the Endstone API.

-----

## 💖 Attribution and Acknowledgements

This plugin was developed with assistance from Artificial Intelligence.

I served as the **System Designer** and **Code Reviewer**, meticulously verifying and debugging the code generated by the AI to ensure stability and performance.

I sincerely hope the community will join in improving this system, helping us make the Minecraft Bedrock Server experience even better for everyone.
