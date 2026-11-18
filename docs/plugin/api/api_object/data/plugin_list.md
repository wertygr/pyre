data.plugin_list:

type: `set[str]`

The names of the plugins that are currently loaded. It is updated automatically:

- `load_plugin` and [hook_dispatch](../hook_dispatch.md) add the plugin name;
- `unload_plugin` (the `_._ unload_plug` command) removes it.

The shell command `_._ ls_plug` prints this set, and the `_._ unload_plug` completer builds its suggestions from it.

<details> <summary> example </summary>

```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    data = api["data"]
    print(data.plugin_list)
```

```pycon
>>> _._ ls_plug
{'example_plugin'}
```

</details>

<details> <summary> read also </summary>

* [unload_plug](../../../../commands/shell_commands/unload_plug.md)
* [hook_dispatch](../hook_dispatch.md)
* [plugin specification](../../../plugin_specification.md)

</details>
