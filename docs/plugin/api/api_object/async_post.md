This function puts an item into the queue of an [async plugin](../../plugin_async.md) from the REPL thread.
The item is delivered in a thread-safe way: `loop.call_soon_threadsafe(queue.put_nowait, item)`.

<details> <summary> signature </summary>

```python
def async_post(data: Data, plugin_name: str, item: Any) -> bool:
    ...
```

| parametr    | description                                                      |
|:------------|-----------------------------------------------------------------:|
| data        | REPL state, see [data](data/data.md)                             |
| plugin_name | name of the async plugin, the key in [plugin_space](../../plugin_space.md) |
| item        | any object, delivered to the coroutine as is                     |

returns `True` if the item was scheduled, `False` if the async thread is not running or the queue was not found.

</details>

<details> <summary> queue lookup </summary>

The queue is taken from [plugin_space](../../plugin_space.md) and must be an `asyncio.Queue`:

- `plugin_space[plugin_name]["queue"]`, if the value is a dict;
- `plugin_space[plugin_name].queue`, otherwise.

`False` is returned right after `_._ async_run`, until `async_main` has created the queue.

</details>

<details> <summary> example </summary>

```python
import asyncio

from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)

PLUGIN_NAME = "_echo_"

async def async_main(api: PluginApi, plugin_space: dict) -> None:
    plugin_space[PLUGIN_NAME] = {"queue": asyncio.Queue()}
    while True:
        item = await plugin_space[PLUGIN_NAME]["queue"].get()
        print(f"[echo] {item}")

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    data = api["data"]
    if command_context["argv"][0] == "_._":
        return
    if not api["async_post"](data, PLUGIN_NAME, command_context["postfix"]):
        api["post"]("[echo]: not running", data)
```

```pycon
>>> _._ async_start
>>> _._ async_run _echo_
>>> _echo_ hello
[echo] hello
```

</details>

<details> <summary> read also </summary>

* [plugin async](../../plugin_async.md)
* [post](post.md)
* [data](data/data.md)

</details>
