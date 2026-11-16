import sys

def base_destructor(package: str|None) -> None: # __package__
    if not package:
        return
    prefix = f"{package}."
    for module in list(sys.modules):
        if module == package or module.startswith(prefix):
            sys.modules.pop(module, None)

__all__ = ["base_destructor"]