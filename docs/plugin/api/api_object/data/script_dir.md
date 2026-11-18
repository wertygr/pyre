data.script_dir:

type: `str`

Absolute path to the directory that contains the pyre kernel file (`pyre.py`). It is set once at startup:

```python
data.script_dir = os.path.dirname(os.path.abspath(__file__))
```

The kernel uses it to locate the `plugins` folder. A plugin can use it to resolve paths relative to the kernel instead of the current working directory.

<details> <summary> example </summary>

```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)
import os

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    data = api["data"]
    plugin_dir = os.path.join(data.script_dir, "plugins")
    print(plugin_dir)
```

</details>

<details> <summary> read also </summary>

* [plugin specification](../../../plugin_specification.md)

</details>
