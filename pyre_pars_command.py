import shlex

from pyre_alias import alias_parser
from pyre_core import Data, post, command_separators


def pars_command(data: Data, final_pars: bool = True, text: str = "") -> list[list[str]]:
    result = []
    if final_pars:
        text = data.command

    if data.settings["shlex"]:
        try:
            argv = shlex.split(text, posix=bool(data.settings["posix"]))
        except ValueError as e:
            if final_pars:
                post(e, data)
            return []
    else:
        argv = text.split()

    if not len(argv):
        if final_pars:
            e = "[pars_command]: not enough arguments"
            post(e, data)
        return []
    if data.settings["alias_globals"]:
        argv = alias_parser(data.settings["alias_dict"], argv, "global")
    if data.settings["separator"]:
        commands = command_separators(argv)
        for i in commands:
            if data.settings["alias_locals"]:
                argv = alias_parser(data.settings["alias_dict"], i, "local")
            result.append(argv)
    else:
        if data.settings["alias_locals"]:
            i = alias_parser(data.settings["alias_dict"], argv, "local")
        else:
            i = argv
        argv = i
        result.append(argv)
    return result