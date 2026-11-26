import asyncio
import inspect
import threading
import time
from concurrent import futures
from typing import Any, TypeVar

from plugins.plugin_tools.lib.base import PluginExit

from pyre_core import (
    Data,
    post,
)
from pyre_const import (
    STOP_TIMEOUT,
    BEAT_INTERVAL,
)

T = TypeVar("T")

def _plugin_error(data: Data, plugin_name: str, e: BaseException) -> None:
    if isinstance(e, PluginExit):
        return
    e.add_note(f"[async_plugin]: {plugin_name}")
    post(e, data, use_hook=False)

def _task_done(data: Data, plugin_name: str, task: Any) -> None:
    if not task.cancelled():
        e = task.exception()
        if e is not None:
            _plugin_error(data, plugin_name, e)
    # a cancelled Task is reported by async_del / async_stop once asyncio.wait() has resolved it
    future = data.async_state.future.pop(plugin_name, None)
    if future is not None and future.set_running_or_notify_cancel():
        future.set_result(None)
    data.async_state.task.pop(plugin_name, None)
    data.async_state.started.pop(plugin_name, None)
    data.plugin_list.discard(plugin_name)

def _cancel_forced(data: Data, plugin_name: str, task: Any|None) -> None:
    # A Task that kept await-ing after cancel() completed its finally block; one stuck in
    # synchronous code is cancelled by asyncio.wait_for and never finishes it.
    if task is not None and task.cancelled() and not task.done():
        _plugin_error(data, plugin_name, asyncio.CancelledError(
            f"[async_plugin]: {plugin_name} stopped before its finally block finished"))

async def _loop_beat(data: Data) -> None:
    while True:
        data.async_state.beat = time.monotonic()
        await asyncio.sleep(BEAT_INTERVAL)

async def _cancel_all(data: Data, timeout: float) -> list[tuple[str, Any]]:
    plugins = sorted(data.async_state.plugin)
    tasks = {i: data.async_state.task.get(i) for i in plugins}
    data.async_state.plugin.clear()
    data.async_state.task.clear()
    data.async_state.started.clear()
    data.plugin_list.difference_update(plugins)
    futures_set = list(data.async_state.future.values())
    data.async_state.future.clear()
    live = [t for t in tasks.values() if t is not None]
    for task in live:
        task.cancel()
    if live:
        pending = set(live)
        deadline = time.monotonic() + timeout
        # asyncio.wait does not cancel: retry cancel() so a Task stuck in synchronous code
        # wakes up and finishes its own finally block
        while pending and time.monotonic() < deadline:
            _, pending = await asyncio.wait(pending, timeout=max(0.0, deadline - time.monotonic()))
            for task in pending:
                task.cancel()
    for future in futures_set:
        if future.set_running_or_notify_cancel():
            future.set_result(None)
    return [(i, t) for i, t in tasks.items() if t is None or t.done()]

def _loop_run(data: Data) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data.async_state.loop = loop
    beat = loop.create_task(_loop_beat(data))
    try:
        loop.run_forever()
    finally:
        beat.cancel()
        try:
            loop.run_until_complete(beat)
        except BaseException:
            pass
        data.async_state.loop = None
        data.async_state.beat = 0.0
        loop.close()

def _loop_ready(data: Data) -> bool:
    return data.async_state.loop is not None and data.async_state.thread is not None and data.async_state.thread.is_alive()

def _stuck_for(data: Data) -> float:
    if not _loop_ready(data) or not data.async_state.beat:
        return 0.0
    return max(0.0, time.monotonic() - data.async_state.beat)

def _stuck_name(data: Data, delay: float) -> str:
    for name in sorted(data.async_state.started):
        if (time.monotonic() - data.async_state.started[name]) >= delay:
            return name
    return ",".join(sorted(data.async_state.plugin))

def async_start(data: Data) -> None:
    # Always clear loop-bound state; if old thread is still alive it will die on its own
    data.async_state.loop = None
    data.async_state.task.clear()
    data.async_state.future.clear()
    data.async_state.started.clear()
    data.async_state.beat = 0.0
    # Also clear async_plugin to prevent stale entries when old thread lingers
    data.async_state.plugin.clear()
    data.plugin_list.difference_update(data.async_state.plugin)
    data.async_state.thread = threading.Thread(target=_loop_run, args=(data,), name="pyre-async", daemon=True)
    data.async_state.thread.start()

def async_run(data: Data, plugin_name: str, module: Any) -> None:
    if not _loop_ready(data):
        post("[async_run]: async thread is not running(use: _._ async_start)", data)
        return
    if plugin_name in data.async_state.plugin:
        post(f"[async_run]: plugin {plugin_name} is already running", data)
        return
    async_main = getattr(module, "async_main", None)
    if async_main is None:
        post(f"[async_run]: plugin {plugin_name} has no async_main", data)
        return
    if not inspect.iscoroutinefunction(async_main):
        post(f"[async_run]: {plugin_name}.async_main is not a coroutine function", data)
        return
    future: futures.Future = futures.Future()

    def submit() -> None:
        coroutine = async_main(
            api=data.api if data.settings.get("plugin", {}).get(plugin_name, {}).get("api", False) else {},
            plugin_space=data.plugin_space,
        )
        if data.async_state.plugin.get(plugin_name) is not future:
            coroutine.close()  # async_del ran before the loop picked the task up
            return
        task = data.async_state.loop.create_task(coroutine)
        data.async_state.task[plugin_name] = task
        data.async_state.started[plugin_name] = time.monotonic()
        # submitted through the loop too: _task_done does not touch asyncio at all
        task.add_done_callback(lambda t: data.async_state.loop.call_soon_threadsafe(_task_done, data, plugin_name, t))

    data.async_state.loop.call_soon_threadsafe(submit)
    data.async_state.plugin[plugin_name] = future
    data.async_state.future[plugin_name] = future
    data.plugin_list.add(plugin_name)

def async_del(data: Data, plugin_name: str) -> None:
    future = data.async_state.plugin.pop(plugin_name, None)
    if future is None:
        return
    data.plugin_list.discard(plugin_name)
    task = data.async_state.task.get(plugin_name)
    if task is not None:
        task.cancel()
    try:
        future.result(STOP_TIMEOUT)
    except futures.TimeoutError:
        post(f"[async_del]: plugin {plugin_name} did not stop in time(max: {STOP_TIMEOUT}s)", data)
    except Exception:
        pass  # the error itself is already posted by _task_done
    data.async_state.future.pop(plugin_name, None)
    if task is not None and task.done():  # a running Task is reported by its own done callback
        _cancel_forced(data, plugin_name, task)

def async_stop(data: Data) -> None:
    if not _loop_ready(data):
        post("[async_stop]: async thread is not running", data)
        return
    loop = data.async_state.loop
    cancel = asyncio.run_coroutine_threadsafe(_cancel_all(data, STOP_TIMEOUT), loop)
    resolved: list[tuple[str, Any]] = []
    stuck: list[str] = []
    try:
        resolved = cancel.result(STOP_TIMEOUT + 1)
        stuck = [i for i, t in resolved if t is not None and not t.done()]
    except futures.TimeoutError:
        stuck = sorted(data.async_state.plugin)
    except Exception as e:
        post(e, data)
    for plugin_name, task in resolved:
        _cancel_forced(data, plugin_name, task)
    if stuck:
        post(f"[async_stop]: plugin did not stop in time: {', '.join(stuck)}", data)
    loop.call_soon_threadsafe(loop.stop)
    data.async_state.thread.join(STOP_TIMEOUT)
    if data.async_state.thread.is_alive():
        post("[async_stop]: async thread did not stop in time", data)
        data.async_state.plugin.clear()
        data.async_state.future.clear()
        data.async_state.task.clear()
        data.async_state.started.clear()
        data.async_state.loop = None
        data.async_state.thread = None
        return
    data.async_state.loop = None
    data.async_state.thread = None

def async_status(data: Data) -> dict[str, Any]:
    queue = {}
    for name in data.async_state.plugin:
        plugin_data = data.plugin_space.get(name)
        q = plugin_data.get("queue") if isinstance(plugin_data, dict) else getattr(plugin_data, "queue", None)
        if isinstance(q, asyncio.Queue):
            queue[name] = q.qsize()
    return {
        "thread": _loop_ready(data),
        "stuck": round(_stuck_for(data), 1),
        "plugin": sorted(data.async_state.plugin),
        "queue": queue,
    }

def async_post(data: Data, plugin_name: str, item: Any) -> bool:
    plugin_data = data.plugin_space.get(plugin_name)
    if isinstance(plugin_data, dict):
        queue = plugin_data.get("queue")
    else:
        queue = getattr(plugin_data, "queue", None)
    if not _loop_ready(data) or not isinstance(queue, asyncio.Queue):
        return False
    if queue._loop is not None and queue._loop is not data.async_state.loop:
        return False
    try:
        data.async_state.loop.call_soon_threadsafe(queue.put_nowait, item)
    except RuntimeError:
        return False
    return True

__all__ = [
    "async_start",
    "async_run",
    "async_del",
    "async_stop",
    "async_status",
    "async_post",
]
