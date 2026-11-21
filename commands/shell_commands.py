import os
import sys
import linecache
from collections import deque
from functools import partial

from pyre_plug_load import unload_plugin, load_plugin, _plugin_cache_load, load_module
from pyre_async import (
    async_start,
    async_run,
    async_del,
    async_stop,
    async_status,
)
from pyre_core import (
    post,
    buffer,
    Data,
    pft,
    require_args,
    text_mapping,
)
from pyre_const import SETTINGS_FILE

_write_modes = (lambda mode, data:
    post(f"[shell_command::buffer_command[{mode}]]: not enough arguments", data) if data.argc < 4 else
    buffer(data, mode, data.argv[3])
)

@require_args(3)
def _buffer_command(data: Data):
    {
        "read": lambda: pft(buffer(data, "read"), data, end=""),
        "write": lambda: _write_modes("write", data),
        "write_add": lambda: _write_modes("write_add",data),
        "clean": lambda: buffer(data,"write", "")
    }.get(data.argv[2], lambda: post(f"[shell_command::buffer_command]: unknown subcommand: {data.argv[2]}", data))()
@require_args(3)
def _read_vf(data: Data):
    if not(data.argv[2] in linecache.cache):
        e = f"[shell_command::read_vf]: not virtual file: {data.argv[2]}"
        post(e, data)
        return
    text = "".join(linecache.getlines(data.argv[2]))
    text_mapping(text, data, data.argv[2:])
@require_args(3)
def _del_vf(data: Data):
    for i in data.argv[2:]:
        if not(i in linecache.cache):
            e = f"[shell_command::del_vf]: not virtual file: \"{i}\""
            post(e, data)
            continue
        del linecache.cache[i]
@require_args(4)
def _hook_run(data: Data):
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
def _run_script(data: Data):
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
def _async_run(data: Data):
    plugin_name = data.argv[2]
    settings = data.settings["plugin"].get(plugin_name)
    if not settings:
        post(f"[shell_command::async_run]: plugin: {plugin_name} does not exist", data)
        return
    if plugin_name in data.async_plugin:
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
@require_args(3)
def _async_del(data: Data):
    for i in data.argv[2:]:
        if i not in data.async_plugin:
            post(f"[shell_command::async_del]: plugin {i} is not running in async mode", data)
            continue
        async_del(data, i)
@require_args(2)
def _async_start(data: Data):
    async_start(data)
@require_args(2)
def _async_stop(data: Data):
    async_stop(data)
@require_args(2)
def _async_ls(data: Data):
    status = async_status(data)
    rows = [f"thread: {'running' if status['thread'] else 'stopped'}"]
    rows.extend(f"{i} - async" for i in status["plugin"])
    text_mapping("\n".join(rows), data.argv[2:], data)

shell_commands_map = {
    "clear": lambda _: os.system("cls") if os.name == "nt" else print("\033c", end=""),
    "exit": lambda _: sys.exit(0),
    "settings_reload": lambda data: data.api["settings_load"](data, SETTINGS_FILE if data.argc < 3 else data.argv[2]),
    "run": _run_script,
    "read_vf": _read_vf,
    "del_vf": _del_vf,
    "unload_plug": lambda data: deque(map(partial(unload_plugin, data=data), data.argv[2:]),maxlen=0),
    "critical_error": _critical_error,
    "hook_run": _hook_run,
    "load_plug": lambda data: deque(map(partial(load_plugin, data), data.argv[2:]), maxlen=0),
    "buffer": _buffer_command,
    "ls_vf": lambda data: text_mapping("\n".join(f"{i} - {sum(len(line) for line in linecache.getlines(i))} char" for i in linecache.cache), data.argv[2:], data),
    "ls_plug": lambda data: text_mapping("\n".join(data.plugin_list), data.argv[2:], data),
    "async_start": _async_start,
    "async_run": _async_run,
    "async_del": _async_del,
    "async_stop": _async_stop,
    "async_ls": _async_ls,
}

@require_args(2)
def shell_command(data: Data) -> None:
    shell_commands_map.get(data.argv[1], lambda _: post(f"[shell_command]: unknown command: {data.argv[1]}", data))(data)