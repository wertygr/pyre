from pyre_core import (
    post,
    Data,
    require_args,
    reverse_search_flag,
    text_mapping,
)

from commands._pyre_inspect import get_source_code, PyreInspectError

@require_args(2)
def source_code(data: Data) -> None:
    obj = data.argv[1]
    flags = data.argv[2:]
    mode = reverse_search_flag({"signature", "code", "dis", "info", "ast"}, flags, "code")
    code = get_source_code(
        obj_name=obj,
        namespace=data.repl_mode,
        mode=mode,
        use_unwrap="unwrap" in flags,
        use_closure="closure" in flags,
        use_eval=not "not_eval" in flags
    )
    if isinstance(code, PyreInspectError):
        post(f"[source_code]: {str(code)}", data)
        return
    text_mapping(code, flags, data)