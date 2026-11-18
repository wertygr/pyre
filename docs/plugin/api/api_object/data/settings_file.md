data.settings_file:

type: `str`

Absolute path to the settings file that is currently loaded. It is set by [settings_load](../settings_load.md) every time settings are loaded, so a plugin can persist its own settings into the same file the user is running with instead of hardcoding `.pyre_settings.json`:

```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)
import json

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    data = api["data"]
    with open(data.settings_file, encoding="utf-8") as f:
        settings = json.load(f)
    settings["prompt"] = ">>>> "
    with open(data.settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
```

This is especially useful when the kernel is started with an alternative settings file (`_._ settings_reload .settings.json`): `data.settings` already reflects that file, and `data.settings_file` points to it.

<details> <summary> read also </summary>

* [settings](settings.md)
* [settings_load](../settings_load.md)
* [settings.md](../../../../settings/settings.md)

</details>
