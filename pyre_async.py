import asyncio
import inspect
import threading
from typing import Any, Coroutine, TypeVar

from pyre_core import (
    Data,
    post,
)

T = TypeVar("T")

STOP_TIMEOUT = 5

def _plugin_error(data: Data, plugin_name: str, e: BaseException) -> None:
    e.add_note(f"[async_plugin]: {plugin_name}")
    post(e, data, use_hook=False)

def _future_done(data: Data, plugin_name: str, future: Any) -> None:
    e = None if future.cancelled() else future.exception()
    if e is not None:
        _plugin_error(data, plugin_name, e)
    if data.async_plugin.get(plugin_name) is future:
        data.async_plugin.pop(plugin_name, None)
        data.plugin_list.discard(plugin_name)

def _loop_run(data: Data) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data.async_loop = loop
    try:
        loop.run_forever()
    finally:
        loop.close()

def _loop_ready(data: Data) -> bool:
    return data.async_loop is not None and data.async_thread is not None and data.async_thread.is_alive()

def _loop_put(loop: asyncio.AbstractEventLoop, coroutine: Coroutine[Any, Any, T]) -> asyncio.Future[T]:
    return asyncio.run_coroutine_threadsafe(coroutine, loop)

def async_start(data: Data) -> None:
    if _loop_ready(data):
        post("[async_start]: async thread is already running", data)
        return
    data.async_loop = None
    data.async_thread = threading.Thread(target=_loop_run, args=(data,), name="pyre-async", daemon=True)
    data.async_thread.start()

def async_run(data: Data, plugin_name: str, module: Any) -> None:
    if not _loop_ready(data):
        post("[async_run]: async thread is not running(use: _._ async_start)", data)
        return
    if plugin_name in data.async_plugin:
        post(f"[async_run]: plugin {plugin_name} is already running", data)
        return
    async_main = getattr(module, "async_main", None)
    if async_main is None:
        post(f"[async_run]: plugin {plugin_name} has no async_main", data)
        return
    if not inspect.iscoroutinefunction(async_main):
        post(f"[async_run]: {plugin_name}.async_main is not a coroutine function", data)
        return
    future = _loop_put(data.async_loop, async_main(
        api=data.api if data.settings.get("plugin", {}).get(plugin_name, {}).get("api", False) else {},
        plugin_space=data.plugin_space,
    ))
    future.add_done_callback(lambda f: _future_done(data, plugin_name, f))
    data.async_plugin[plugin_name] = future
    data.plugin_list.add(plugin_name)

def async_del(data: Data, plugin_name: str) -> None:
    future = data.async_plugin.pop(plugin_name, None)
    if future is None:
        return
    data.plugin_list.discard(plugin_name)
    future.cancel()
    try:
        future.exception(STOP_TIMEOUT)
    except BaseException:
        pass

def async_stop(data: Data) -> None:
    if not _loop_ready(data):
        post("[async_stop]: async thread is not running", data)
        return
    for plugin_name in list(data.async_plugin):
        async_del(data, plugin_name)
    loop = data.async_loop
    loop.call_soon_threadsafe(loop.stop)
    data.async_thread.join(STOP_TIMEOUT)
    if data.async_thread.is_alive():
        post("[async_stop]: async thread did not stop in time", data)
        return
    data.async_loop = None
    data.async_thread = None

def async_status(data: Data) -> dict[str, Any]:
    return {
        "thread": _loop_ready(data),
        "plugin": sorted(data.async_plugin),
    }

def async_post(data: Data, plugin_name: str, item: Any) -> bool:
    plugin_data = data.plugin_space.get(plugin_name)
    if isinstance(plugin_data, dict):
        queue = plugin_data.get("queue")
    else:
        queue = getattr(plugin_data, "queue", None)
    if not _loop_ready(data) or not isinstance(queue, asyncio.Queue):
        return False
    data.async_loop.call_soon_threadsafe(queue.put_nowait, item)
    return True

__all__ = [
    "async_start",
    "async_run",
    "async_del",
    "async_stop",
    "async_status",
    "async_post",
]
