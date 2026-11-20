Function manually working with the internal buffer(wrapper around [data._buffer](data/_buffer.md)).
The buffer can trigger hooks
<details> <summary> signature </summary> 

buffer(data: Data, mode: str, text: str = "", use_hook: bool = True) -> str|None

</details>

<details> <summary> example </summary>

code:
```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    buffer = api["buffer"]
    data = api["data"]
    """
    arg_0 - data
    arg_1 - mode(type str) "write"/"write_add"/"read"
    arg_2 - Optional[text(type str)]
    arg_3 - Optional[use_hook(type bool)]
    
    mode="read"        - read buffer
    mode="write_aad"   - add to buffer
    mode="write"       - write to buffer
    """
    print(buffer(data, "read"))
```
example use:
```pycon
>>> _#_ settings["shlex"] == True = True
>>> _._ buffer write "0 1 2 3 4 5 6 7 8 9"
>>> _test_
0 1 2 3 4 5 6 7 8 9
>>>
```
</details>

<details> <summary> read also </summary>

[data._buffer](data/_buffer.md)
[buffer system hook](../../hook/system_hooks/buffer.md)
</details>