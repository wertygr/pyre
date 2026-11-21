**async plugins:**

An async plugin keeps a coroutine running in a background thread, so a long job (sockets, network requests, polling) does not block the REPL.

> [!WARNING]
> There is no sandbox, and the coroutine shares the process with the REPL. A blocking call inside `async_main` freezes **all** async plugins.

<details> <summary> how it works </summary>

- `_._ async_start` creates one daemon thread (`pyre-async`) with one `asyncio` event loop. All async plugins share it.
- `_._ async_run <plugin>` schedules `async_main` of the plugin on that loop (`asyncio.run_coroutine_threadsafe`).
- Async mode is always started explicitly. There is no `async` key in the plugin settings.
- The thread, the loop and the running plugins are stored in [data](api/api_object/data/data.md): `async_thread`, `async_loop`, `async_plugin`.

</details>

<details> <summary> contract </summary>

A plugin becomes async when its module has a coroutine function `async_main` (checked with `inspect.iscoroutinefunction`).
It is called with two keyword arguments:

- 1 [API](api/api.md): dict (`{}` if `"api": false` in the plugin settings)
- 2 [plugin_space](plugin_space.md): dict

```python
from plugins.plugin_tools.plugin_types import PluginApi

async def async_main(api: PluginApi, plugin_space: dict) -> None:
    ...
```

The coroutine runs until it returns, raises, or is cancelled by `async_del`, `async_stop` or `unload_plug`.
Put resource cleanup (sockets, files) into `try/finally`: cancellation arrives as `CancelledError` at the current `await`.

The plugin still needs a normal `main`: it is the command interface (sending data to the coroutine, showing status).
Use `"cache": true` in the settings.

</details>

<details> <summary> commands </summary>

| command                     | argc | description                                                       |
|:----------------------------|:----:|:------------------------------------------------------------------|
| `_._ async_start`           |  2   | start the background thread and event loop                        |
| `_._ async_run <plugin>`    |  3   | load the plugin if needed and start its `async_main`              |
| `_._ async_del <plugin>...` |  3   | cancel the coroutine(s), waits up to 5 s for `finally`            |
| `_._ async_stop`            |  2   | cancel all coroutines, stop the loop, join the thread (up to 5 s) |
| `_._ async_ls`              |  2   | thread state and running async plugins                            |

```pycon
>>> _._ async_ls
thread: running
_echo_ - async
```

A running async plugin is also listed in [plugin_list](api/api_object/data/plugin_list.md).
`_._ unload_plug` cancels the coroutine first, then runs the usual unload (see below).

> [!NOTE]
> If the plugin is not loaded yet, `async_run` loads the module the usual way, and that **calls `main`** with the `async_run` command line
> (`argv[0] == "_._"`). Ignore such a call in `main` (see the example).

</details>

<details> <summary> talking to the coroutine </summary>

Send data to the coroutine with [async_post](api/api_object/async_post.md):

```python
api["async_post"](data, plugin_name, item) -> bool
```

Create the queue inside `async_main`: an `asyncio.Queue` is bound to the event loop on first use, so a queue reused after `async_stop` + `async_start` belongs to the old loop.

</details>

<details> <summary> example </summary>

```python
# ./plugins/echo.py
import asyncio

from plugins.plugin_tools.plugin_types import PluginApi, CommandContext

PLUGIN_NAME = "_echo_"

def destructor(plugin_space: dict) -> None:
    plugin_space.pop(PLUGIN_NAME, None)

async def async_main(api: PluginApi, plugin_space: dict) -> None:
    state = plugin_space[PLUGIN_NAME] = {"queue": asyncio.Queue(), "count": 0}
    try:
        while True:
            item = await state["queue"].get()
            state["count"] += 1
            print(f"[echo] {item}")
    finally:
        pass  # close sockets / files here

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    data = api["data"]
    if command_context["argv"][0] == "_._":  # loaded by `_._ async_run`
        return
    if not api["async_post"](data, PLUGIN_NAME, command_context["postfix"]):
        api["post"]("[echo]: not running(use: _._ async_start + _._ async_run _echo_)", data)
```

```json
{
    "plugin": {
        "_echo_": {"file": "echo.py", "cache": true, "api": true}
    }
}
```

```pycon
>>> _._ async_start
>>> _._ async_run _echo_
>>> _echo_ hello
[echo] hello
>>> _._ async_del _echo_
```

</details>

<details> <summary> unload and destructor </summary>

`_._ unload_plug <plugin>` does, in this order:

1. cancels the coroutine and waits up to 5 s for its `finally`;
2. removes the module from [repl_mode](api/api_object/data/repl_mode.md);
3. calls the [destructor](plugin_destructor.md) and removes the module from `sys.modules`;
4. removes the name from `plugin_list`.

Close live resources in the `finally` of `async_main`, not in the destructor: the destructor only cleans `plugin_space`.
`_._ async_stop` does not run destructors. Process exit does not run `finally` of daemon threads, so run `_._ async_stop` first if cleanup matters.

</details>

<details> <summary> rules </summary>

- Never block the loop: use `await asyncio.sleep`, `asyncio.open_connection`, `AsyncOpenAI`, not `time.sleep`, `socket.recv`, `requests`.
- Do not read `data.argv`, `data.command`, `data.postfix` from the coroutine: the REPL overwrites them on every command. Copy what you need.
- Keep state in `plugin_space[PLUGIN_NAME]`.
- Output from the coroutine: plain `print()` works with the prompt. Do not call `pft` or `post` from the coroutine yourself.
- Settings are read at `async_run` time (the `api` flag); `settings_reload` does not affect running coroutines.

</details>

<details> <summary> errors </summary>

An exception in `async_main` is passed to `post` with the note `[async_plugin]: <name>`. The plugin is removed from `plugin_list`, and the thread keeps running.

| message                                                                  | cause                                       |
|:-------------------------------------------------------------------------|:--------------------------------------------|
| `[async_start]: async thread is already running`                         | second `async_start`                        |
| `[async_run]: async thread is not running(use: _._ async_start)`         | `async_run` before `async_start`            |
| `[shell_command::async_run]: plugin <name> is already running`           | second `async_run`                          |
| `[async_run]: plugin <name> has no async_main`                           | no `async_main` in the module               |
| `[async_run]: <name>.async_main is not a coroutine function`             | `async_main` is a plain `def`               |
| `[shell_command::async_del]: plugin <name> is not running in async mode` | `async_del` on a plugin that is not running |
| `[async_stop]: async thread is not running`                              | `async_stop` without a thread               |
| `[async_stop]: async thread did not stop in time`                        | the loop did not stop within 5 s            |

</details>

***
<details> <summary> read also </summary>

* [plugin](plugin.md)
* [plugin_space](plugin_space.md)
* [plugin destructor](plugin_destructor.md)
* [plugin API](api/api.md)
* [async_post](api/api_object/async_post.md)
</details>
