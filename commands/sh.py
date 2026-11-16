import subprocess

from pyre_core import (
    post,
    Data,
)


def _sh_parser(argv: list[str], name_space: dict) -> list[str]:
    result = []
    for arg in argv:
        if arg.startswith("$"):
            if arg[1:] in name_space:
               result.append(str(name_space[arg[1:]]))
            else:
                result.append(arg)
        else:
            result.append(arg)
    return result
def sh(data: Data) -> None:
    shell = data.settings["shell"]
    shell_container = data.settings["shell_container"]
    args = _sh_parser(data.argv[1:], data.repl_mode) if shell_container else data.argv[1:]
    try:
        subprocess.run(
            args if not shell else " ".join(args),
            shell=shell
        )
    except FileNotFoundError:
        post(f"[sh]: not file program: {args[0]}", data)
