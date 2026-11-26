from enum import Enum
from inspect import CO_GENERATOR, CO_ASYNC_GENERATOR, CO_COROUTINE
from typing import Callable

SUPPORTED_ASYNC_PLUGINS: bool = True

_FN_TYPE_MASK = (
    CO_GENERATOR | CO_COROUTINE | CO_ASYNC_GENERATOR
)

def fn_convert(fn: Callable) -> FnType:
    if not callable(fn):
        raise TypeError(f"{fn!r} is not a callable object")
    func = getattr(fn, "__func__", fn)
    code = getattr(func, "__code__", None)
    if code is None:
        return FnType.SYNC
    return FnType(code.co_flags & _FN_TYPE_MASK)

class FnType(Enum):
    SYNC = 0
    ASYNC = CO_COROUTINE
    GEN = CO_GENERATOR
    ASYNC_GEN = CO_ASYNC_GENERATOR

    def is_i(self, fn: Callable) -> bool:
        return self == fn_convert(fn)

class MagicFunction(Enum):
    MAIN =       ("main",       FnType.SYNC)
    HOOK_RUN =   ("hook_run",   FnType.SYNC)
    DESTRUCTOR = ("destructor", FnType.SYNC)
    ASYNC_MAIN = ("async_main", FnType.ASYNC)

    def __init__(self, name: str, fn_type: FnType):
        self.fn_name = name
        self.fn_type = fn_type

__all__ = [
    "SUPPORTED_ASYNC_PLUGINS",
    "MagicFunction",
    "fn_convert",
    "FnType",
]