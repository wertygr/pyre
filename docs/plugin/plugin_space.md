buffer between plugins

example:

plugin 1:
```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)

PLUGIN_NAME = "_test_"

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    if PLUGIN_NAME not in plugin_space: # init
        plugin_space[PLUGIN_NAME] = {
            "i": 0
        }
    plugin_space[PLUGIN_NAME]["i"] += 1
```

plugin 2:
```python
from plugins.plugin_tools.plugin_types import PluginApi, CommandContext

BUFFER_KEY = "_test_"
def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    print(plugin_space.get(BUFFER_KEY))
```

```pycon
>>> _._ settings_reload .settings.json
>>> _test_
>>> _test_
>>> _test-2_
{'i': 2}
>>> _test_
>>> _test_
>>> _test-2_
{'i': 4}
>>>
```