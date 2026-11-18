data.plugin_space:

type: `dict`

A shared dictionary that plugins use to store their own data between calls. Each plugin should keep its state under its own name to avoid collisions:

```python
plugin_space[PLUGIN_NAME] = {...}
```

The same dictionary is passed to every plugin function as the `plugin_space` argument:

- [main](../../../plugin.md) - `main(api, command_context, plugin_space)`
- [hook_run](../../../hook/hook.md) - `hook_run(api, hook, hook_parameter, plugin_space)`
- [destructor](../../../plugin_destructor.md) - `destructor(plugin_space)`

Unlike [repl_mode](repl_mode.md), the contents of `plugin_space` are not removed automatically when the plugin is unloaded. Clean up your entry in the [destructor](../../../plugin_destructor.md):

```python
def destructor(plugin_space) -> None:
    plugin_space.pop(PLUGIN_NAME, None)
```

<details> <summary> example </summary>

```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)

PLUGIN_NAME = "example_plugin"

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    if PLUGIN_NAME not in plugin_space:
        plugin_space[PLUGIN_NAME] = {"i": 0}
    plugin_space[PLUGIN_NAME]["i"] += 1
    print(plugin_space[PLUGIN_NAME]["i"])
```

</details>

<details> <summary> read also </summary>

* [plugin_space](../../../plugin_space.md)
* [plugin destructor](../../../plugin_destructor.md)

</details>
