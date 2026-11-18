data._pyt_plus_old_text:

type: `str`

Internal buffer of the `_pyt++_` multi-line editor. It stores the text that is currently being edited and lets the text survive between calls of the command:

- `_pyt++_` opens the editor with the previous text as the default value;
- `_pyt++_ old` loads the saved cache into the buffer first;
- `_pyt++_ paste` appends the contents of the [internal buffer](../buffer.md);
- after editing, the buffer is executed and/or saved (`save`, `copy`, `not_exec`, `not_cache` flags).

Plugins normally do not need to touch this field.
