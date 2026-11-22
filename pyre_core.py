import sys
import traceback
import linecache
import threading
from collections import deque
from typing import Any, Callable, TextIO, Literal
from types import TracebackType
from functools import wraps

from plugins.plugin_tools import PluginData
from plugins.plugin_tools.plugin_types import (PluginApi)

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.styles import BaseStyle
from pygments.lexers import PythonLexer
from pygments.lexer import RegexLexer

from pyre_const import SETTINGS_FILE

class AsyncState:
    def __init__(self) -> None:
        self.future: dict[str, Any] = {}
        self.task: dict[str, Any] = {}
        self.started: dict[str, float] = {}
        self.beat: float = 0.0
        self.loop: Any = None
        self.thread: threading.Thread | None = None
        self.plugin: dict[str, Any] = {}

class Data(PluginData):
    def __init__(self) -> None:
        self.last_error: str = ""
        self.repl_mode: dict = {}
        self._repl_cache_id: int = 0
        self.settings: dict = {}
        self.settings_file: str = SETTINGS_FILE
        self.pt_style: BaseStyle
        self.script_dir: str = ""
        self.api: PluginApi = {} # type: ignore
        self.plugin_space: dict = {}
        self._local_repl_mode:dict = {}
        self._pyt_plus_old_text: str = ""
        self.command: str = ""
        self.postfix: str = ""
        self.argc: int = 0
        self.argv: list[str] = []
        self.lexer: type[RegexLexer] = PythonLexer
        self.lexer_instance: RegexLexer = self.lexer()
        self.plugin_list: set[str] = set()
        self._buffer: str = ""
        self.async_state: AsyncState = AsyncState()

NOP = lambda *_, **__: None
type CommandFunc = Callable[[Data], Any]

class CommandMap:
    def __init__(self, command_map: dict[str, CommandFunc], default_hook: CommandFunc|None = None) -> None:
        self.command_map = command_map
        self.default_hook = default_hook
    def __call__(self, key: str, data: Data, error_message: str|None = None) -> None:
        func = self.command_map.get(key)
        if func:
            func(data)
            return
        if self.default_hook:
            self.default_hook(data)
            return
        if error_message:
            post(error_message, data)


def reverse_search_flag(modes: set[str], flags: list[str], def_mode: str)-> str:
    for i in reversed(flags):
        if i in modes:
            return i
    return def_mode

def flag_mapping(flag_map: dict[str, tuple[Callable, bool]], command_args: list[str], *args, **kwargs) -> None:
    args_set = set(command_args)
    deque(
        (action(*args, **kwargs) for flag, (action, run_if_present) in flag_map.items()
         if (flag in args_set) == run_if_present),
        maxlen=0
    )

def text_mapping(text: str, argv: list[str], data: Data):
    flag_mapping({
        "copy": (lambda: buffer(data, "write", text), True),
        "silent": (lambda: pft(text, data, end=""), False),
    }, argv)
def require_args(min_argc: int) -> Callable[[CommandFunc], CommandFunc]:
    def decorator(func: CommandFunc) -> CommandFunc:
        @wraps(func)
        def wrapper(data: Data) -> None:
            if data.argc < min_argc:
                post(f"[{func.__name__}]: not enough arguments(min argc: {min_argc})", data)
                return
            func(data)
        return wrapper
    return decorator

def pft(text: Any, data: Data, end: str= "\n", use_hook: bool = True, file:TextIO = sys.stdout) -> None:
    lexer = data.lexer_instance
    tokens = list(lexer.get_tokens(str(text)))
    print_formatted_text(
        PygmentsTokens(
            tokens
        ),
        style=getattr(data, "pt_style", None),
        end=end,
        include_default_pygments_style=False,
        file=file,
    )
    if use_hook:
        hooks_dispatch = data.api.get("hook_dispatch", NOP)
        hooks_dispatch(data, "pft", {"text": f"{text}"})

def buffer(data: Data, mode: Literal["read", "write", "write_add"], text: str = "", use_hook: bool = True) -> str|None:
    data.api["hook_dispatch"](data, "buffer", {"text": text, "mode": mode}) if use_hook else None
    if mode == "read":
        return data._buffer
    elif mode == "write":
        data._buffer = text
    elif mode == "write_add":
        data._buffer += text

def traceback_format(e: TracebackType|BaseException|str) -> str:
    if isinstance(e, TracebackType):
        e = "".join(traceback.format_tb(e))
    elif isinstance(e, BaseException):
        e = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    return e

def post(e: TracebackType|BaseException|str, data: Data, use_hook: bool = True) -> None:
    is_recursion = isinstance(e, RecursionError)
    if is_recursion:
        sys.setrecursionlimit(sys.getrecursionlimit() + 50)
    e = traceback_format(e)
    if is_recursion:
        sys.setrecursionlimit(sys.getrecursionlimit() - 50)
    data.last_error = e
    if use_hook:
        hooks_dispatch = data.api.get("hook_dispatch", NOP)
        hooks_dispatch(data, "post", {"err": str(e)})
    pft(e, data, use_hook=use_hook)

def command_separators(command_arg: list[str], token: str = "_&_") -> list[list[str]]:
    subarrays = []
    current = []
    for item in command_arg:
        if item == token:
            if current:
                subarrays.append(current)
                current = []
        else:
            current.append(item)

    if current:
        subarrays.append(current)
    return subarrays

def str_is_int(string: str) -> bool:
    if not string:
        return False
    if string[0] in ["+","-"]:
        return string[1:].isdigit()
    return string.isdigit()

def line_num(
        width: int,
        line_number: int,
        is_soft_wrap: int,
        format_sample: str
    ) -> str:
    return format_sample.format(
         width=width,
         line_number=line_number + 1,
         is_soft_wrap=is_soft_wrap
    )

def register_repl_source(source: str, data: Data) -> str:
    data._repl_cache_id += 1
    filename = f"<py_repl_{data._repl_cache_id}>"
    linecache.cache[filename] = (len(source), None, source.splitlines(keepends=True), filename)
    return filename