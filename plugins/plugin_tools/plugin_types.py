from __future__ import annotations
import sys
from types import TracebackType
from typing import TypedDict, Callable, Any, Protocol, TextIO, Literal
from prompt_toolkit.styles import BaseStyle
from pygments.lexer import RegexLexer

class Stringable(Protocol):
    def __str__(self) -> str:
        ...

class OptBuffer(Protocol):
    def __call__(self, data: PluginData, mode: Literal["read", "write", "write_add"], text: str = "", use_hook: bool = True) -> str|None:
        ...

class OptPost(Protocol):
    def __call__(self, e: TracebackType|BaseException|str, data: PluginData, use_hook: bool = True) -> None:
        ...

class OptPft(Protocol):
    def __call__(self, text: Stringable, data: PluginData, end: str = "\n", use_hook: bool = True, file: TextIO = sys.stdout) -> None:
        ...

class OptSettingsLoad(Protocol):
    def __call__(self, data: PluginData, file: str = ".pyre_settings.json") -> None:
        ...

class OptCommandSeparators(Protocol):
    def __call__(self, command_arg: list[str], token: str = "_&_") -> list[list[str]]:
        ...

class OptAliasParser(Protocol):
    def __call__(self, alias_dict: dict, command_arg: list[str], mode: str) -> list[str]:
        ...

class OptRegisterReplSource(Protocol):
    def __call__(self, source: str, data: PluginData) -> str:
        ...

class OptFlagMapping(Protocol):
    def __call__(
        self,
        flag_map: dict[str, tuple[Callable[..., Any], bool]],
        command_args: list[str],
        *args: Any,
        **kwargs: Any
    ) -> None:
        ...

class PluginApi(TypedDict):
    settings_load: OptSettingsLoad
    post: OptPost
    pft: OptPft
    command_separators: OptCommandSeparators
    pars_command: Callable[[PluginData], None]
    dispatcher: Callable[[PluginData], None]
    buffer: OptBuffer
    alias_parser: OptAliasParser
    data: PluginData
    register_repl_source: OptRegisterReplSource
    hook_dispatch: Callable[[PluginData, str, dict], list[Any]]
    traceback_format: Callable[[TracebackType|BaseException|str], str]
    flag_mapping: OptFlagMapping
    reverse_search_flag: Callable[[set[str], list[str], str], str]
    NOP: Callable[..., None]
    require_args: Callable[[int], Callable[[CommandFunc], CommandFunc]]

class CommandContext(TypedDict):
    argv: list[str]
    postfix: str
    argc: int

class PluginSettings(TypedDict, total=False):
    file: str
    api: bool
    cache: bool
    hooks: list[str]

class AliasSettings(TypedDict, total=False):
    scope: str
    position: list[int] | None
    value: list[str]

class Settings(TypedDict, total=True):
    color: dict[str, str]
    plugin: dict[str, PluginSettings]
    alias_dict: dict[str, AliasSettings]
    posix: bool
    shlex: bool
    shell: bool
    vi_mode: bool
    multiline: bool
    separator: bool
    completer: bool
    alias_locals: bool
    mouse_support: bool
    alias_globals: bool
    bottom_toolbar: bool
    shell_container: bool
    prompt: str
    repl_mode: str
    line_name_format: str

class PluginData(Protocol):
    last_error: str
    repl_mode: dict
    _repl_cache_id: int
    settings: Settings
    settings_file: str
    pt_style: BaseStyle
    script_dir: str

    api: PluginApi

    plugin_space: dict
    _local_repl_mode: dict
    _pyt_plus_old_text: str
    _buffer: str

    command: str
    postfix: str
    argc: int
    argv: list[str]

    plugin_list: set[str]

    lexer: type[RegexLexer]
    lexer_instance: RegexLexer

CommandFunc = Callable[[PluginData], None]

__all__ = ["PluginData", "PluginApi", "PluginSettings", "Settings", "AliasSettings", "CommandContext"]