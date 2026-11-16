import os
import types
import datetime

from pyre_prompt_toolkit import make_jedi_completer
from pyre_bottom_toolbar import bottom_toolbar
from pyre_core import (
    post,
    buffer,
    Data,
    line_num,
    register_repl_source,
    pft,
    traceback_format,
    flag_mapping,
)
from pyre_const import PYT_SAVE, PYT_CACHE

from pyre_bindings import bindings
from prompt_toolkit import PromptSession

from prompt_toolkit.lexers import PygmentsLexer

def pyt(data: Data) -> None:
    ev_except = ""
    ex_except = ""
    f_name = register_repl_source(data.postfix, data)
    def byte_code_compile(code: str, mode: str):
        nonlocal ev_except, ex_except
        try:
            return compile(code, f_name, mode)
        except Exception as e:
            if mode == "exec":
                ex_except = e
            else:
                ev_except = e
            return False

    byte_code_ev: types.CodeType|False = byte_code_compile(data.postfix, "eval")
    byte_code_ex: types.CodeType|False = byte_code_compile(data.postfix, "exec")
    if byte_code_ev:
        try:
            pft(eval(byte_code_ev, data.repl_mode), data)
        except Exception as e:
            post(e, data)
    elif byte_code_ex:
        try:
            exec(byte_code_ex, data.repl_mode)
        except Exception as e:
            post(e, data)
    else:
        e = f"{'__ '*15} \neval: \n{traceback_format(ev_except)} \n{'__ '*15}\nexec: \n{traceback_format(ex_except)} \n{'__ '*15}"
        post(e, data)

def pyt_exec(data: Data) -> None:
    f_name = register_repl_source(data.postfix, data)
    try:
        exec(compile(data.postfix, f_name, "exec"), data.repl_mode)
    except Exception as e:
        post(e, data)

def pyt_eval(data: Data) -> None:
    try:
        pft(eval(data.postfix, data.repl_mode), data)
    except Exception as e:
        post(e, data)

def _read_cache(data: Data) -> None:
    if not data._pyt_plus_old_text:
        with open(f"{PYT_SAVE}/{PYT_CACHE}", "r", encoding="utf-8") as f:
            data._pyt_plus_old_text = f.read()

def _save(data: Data) -> None:
    time_now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    try:
        with open(f"{PYT_SAVE}/{time_now}.py", "w") as file:
            file.write(data._pyt_plus_old_text)
            print(f"{time_now}.py")
    except Exception as e:
        post(e, data)

def _save_cache(data: Data) -> None:
    if not os.path.isdir(PYT_SAVE):
        os.mkdir(PYT_SAVE)
    with open(f"{PYT_SAVE}/{PYT_CACHE}", "w") as f:
        f.write(data._pyt_plus_old_text)

def _execute(data: Data) -> None:
    if not data._pyt_plus_old_text:
        return
    f_name = register_repl_source(data._pyt_plus_old_text, data)
    ex_code = (
        lambda: pft(eval(compile(data._pyt_plus_old_text, f_name, "eval"), data.repl_mode), data) if "eval" in data.argv
        else exec(compile(data._pyt_plus_old_text, f_name, "exec"), data.repl_mode)
    )
    try:
        ex_code()
    except Exception as e:
        post(e, data)

def editor(data: Data) -> None:
    edit_session = PromptSession(
        key_bindings=bindings,
    )
    edit_session.app.data = data
    edit_session.app.mode = "pyt++"
    toolbar = lambda: bottom_toolbar(data)
    try:
        data._pyt_plus_old_text = edit_session.prompt(
            line_num(0, 0, 0, data.settings["line_name_format"]),
            default=data._pyt_plus_old_text,
            completer=make_jedi_completer(data) if (not "no_jedi" in data.argv) and not data.settings["completer"] else None,
            lexer=PygmentsLexer(data.lexer),
            style=data.pt_style,
            multiline=True,
            prompt_continuation=lambda w, h, s: line_num(w, h, s, data.settings["line_name_format"]),
            vi_mode=data.settings["vi_mode"],
            mouse_support=data.settings["mouse_support"],
            bottom_toolbar=toolbar() if data.settings["bottom_toolbar"] else None,
        )
    except (KeyboardInterrupt, EOFError):
        data._pyt_plus_old_text = ""

def pyt_pp(data: Data) -> None:
    if "old" in data.argv:
        _read_cache(data)
    else:
        data._pyt_plus_old_text = ""
    if "paste" in data.argv:
        data._pyt_plus_old_text += buffer(data, "read") # type: ignore
    editor(data)

    flag_map = {
        "save": (_save, True),
        "copy": (lambda _: buffer(data, "write", data._pyt_plus_old_text), True),
        "not_exec":(_execute, False),
        "not_cache": (_save_cache, False)
    }
    flag_mapping(flag_map, data.argv[1:], data)