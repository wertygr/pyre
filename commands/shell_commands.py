import os
import sys
import linecache
from collections import deque
from functools import partial

from pyre_commands import PathCompleterType
from pyre_plug_load import unload_plugin, load_plugin, load_module
from pyre_async import (
    async_start,
    async_run,
    async_del,
    async_stop,
    async_status,
)
from pyre_const import STUCK_AFTER, SETTINGS_FILE
from pyre_core import (
    post,
    buffer,
    Data,
    pft,
    require_args,
    text_mapping,
    CommandMap
)

_write_modes = (lambda mode, data:
    post(f"[shell_command::buffer_command[{mode}]]: not enough arguments", data) if data.argc < 4 else
    buffer(data, mode, data.argv[3])
)

_buffer_commands_map = CommandMap({
    "read": lambda data: pft(buffer(data, "read"), data, end=""),
    "write": lambda data: _write_modes("write", data),
    "write_add": lambda data: _write_modes("write_add",data),
    "clean": lambda data: buffer(data,"write", "")
})

@require_args(3)
def _buffer_command(data: Data) -> None:
    _buffer_commands_map(data.argv[2], data,f"[shell_command::buffer_command]: unknown subcommand: {data.argv[2]}")
@require_args(3)
def _read_vf(data: Data) -> None:
    if not(data.argv[2] in linecache.cache):
        e = f"[shell_command::read_vf]: not virtual file: {data.argv[2]}"
        post(e, data)
        return
    text = "".join(linecache.getlines(data.argv[2]))
    text_mapping(text, data.argv[2:], data)
@require_args(3)
def _del_vf(data: Data) -> None:
    for i in data.argv[2:]:
        if not(i in linecache.cache):
            e = f"[shell_command::del_vf]: not virtual file: \"{i}\""
            post(e, data)
            continue
        del linecache.cache[i]
@require_args(4)
def _hook_run(data: Data) -> None:
    hooks_dispatch = data.api["hook_dispatch"]
    hook_name = data.argv[2]
    try:
        # _._ hook_run "name" "{\"test\": \"test hook run\"}"
        hook_arg = eval(data.argv[3], data.repl_mode)
    except Exception as e:
        post(e, data)
        return
    hooks_dispatch(data, hook_name, hook_arg)
def _critical_error(_):
    raise RuntimeError("critical error in core(tester except)")
@require_args(3)
def _run_script(data: Data) -> None:
    path = data.argv[2]
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data.command = line
                data.api["pars_command"](data)
    except Exception as e:
        post(e, data)

@require_args(3)
def _async_run(data: Data) -> None:
    plugin_name = data.argv[3]
    settings = data.settings["plugin"].get(plugin_name)
    if not settings:
        post(f"[shell_command::async_run]: plugin: {plugin_name} does not exist", data)
        return
    if plugin_name in data.async_state.plugin:
        post(f"[shell_command::async_run]: plugin {plugin_name} is already running", data)
        return
    try:
        module = data.repl_mode.get(plugin_name)
        if module is None:
            module = load_module(data, plugin_name)
        if module is None:
            post(f"[shell_command::async_run]: failed to load module: {plugin_name}", data)
        async_run(data, plugin_name, module)
    except Exception as e:
        post(e, data)
def _async_del(data: Data) -> None:
    for i in data.argv[3:]:
        if i not in data.async_state.plugin:
            post(f"[shell_command::async_del]: plugin {i} is not running in async mode", data)
            continue
        async_del(data, i)
def _async_ls(data: Data) -> None:
    status = async_status(data)
    if not status["thread"]:
        thread = "stopped"
    elif status["stuck"] > STUCK_AFTER:
        thread = f"stuck({status['stuck']:.1f}s, in: {', '.join(status['plugin']) or '-'})"
    else:
        thread = "running"
    rows = [f"thread: {thread}"]
    rows.extend(f"{i} - async, queue: {status['queue'].get(i, '-')}" for i in status["plugin"])
    text_mapping("\n".join(rows), data.argv[3:], data)

_async_commands_map = CommandMap({
    "start": async_start,
    "stop": async_stop,
    "ls": _async_ls,
    "run": _async_run,
    "del": _async_del,
})

@require_args(3)
def _async_command(data: Data) -> None:
    command = data.argv[2]
    _async_commands_map(command, data,f"[shell_command::_async_command]: unknown command: {command}")

shell_commands_map = CommandMap({
    "clear": lambda _: os.system("cls") if os.name == "nt" else print("\033c", end=""),
    "exit": lambda _: sys.exit(0),
    "settings_reload": (
        lambda data: data.api["settings_load"](data, SETTINGS_FILE if data.argc < 3 else data.argv[2]),
        PathCompleterType(),
    ),
    "run": (_run_script, PathCompleterType()),
    "read_vf": (_read_vf, lambda state: list(linecache.cache.keys())),
    "del_vf": (_del_vf, lambda state: list(linecache.cache.keys())),
    "unload_plug": (
        lambda data: deque(map(partial(unload_plugin, data=data), data.argv[2:]), maxlen=0),
        lambda state: state.data.plugin_list,
    ),
    "critical_error": _critical_error,
    "hook_run": _hook_run,
    "load_plug": (
        lambda data: deque(map(partial(load_plugin, data), data.argv[2:]), maxlen=0),
        lambda state: state.data.settings["plugin"].keys(),
    ),
    "buffer": _buffer_command,
    "ls_vf": lambda data: text_mapping("\n".join(f"{i} - {sum(len(line) for line in linecache.getlines(i))} char" for i in linecache.cache), data.argv[2:], data),
    "ls_plug": (lambda data: text_mapping("\n".join(data.plugin_list), data.argv[2:], data),
                ("copy", "silent")
               ),
    "async": _async_command
}, prefix=("_._", ))

@require_args(2)
def shell_command(data: Data) -> None:
    shell_commands_map(data.argv[1], data,f"[shell_command]: unknown command: {data.argv[1]}")