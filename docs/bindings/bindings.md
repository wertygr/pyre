**bindings:**

Key bindings are configured in the [pyre_bindings.py](../../pyre_bindings.py) file.\
The same `KeyBindings` object is used by the main REPL and by the multiline editor [\_pyt++\_](../commands/pyt_pp.md).

<details> <summary> current bindings </summary>

| key                  | action               | description                                                                                                                                           |
|:---------------------|:---------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Ctrl+Q`<br/>(`c-q`) | clear buffer         | removes all text from the current input buffer without executing it                                                                                   |
| `Ctrl+W`<br/>(`c-w`) | delete previous word | calls the prompt_toolkit [`unix_word_rubout`](https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/key_bindings.html) command |

These bindings work both in the REPL prompt and in the `_pyt++_` editor.

</details>

<details> <summary> standard keys </summary>

Keys that are not defined in `pyre_bindings.py` are handled by the standard prompt_toolkit bindings. For example:

| key         | action                                                                            |
|:------------|:----------------------------------------------------------------------------------|
| `Enter`     | accept the command in the REPL; insert a newline in the multiline editor          |
| `Esc+Enter` | accept and close the multiline editor (`_pyt++_`)                                 |
| `Ctrl+C`    | cancel input; in `_pyt++_` the editor is closed and the entered text is discarded |
| `Ctrl+D`    | end of input                                                                      |

</details>

<details> <summary> how to add a binding </summary>

A binding is a function decorated with `bindings.add(...)`. The key is written in prompt_toolkit notation: `c-` is `Ctrl`, `escape` is `Alt`, and named keys such as `enter`, `escape`, `up` or `f1` are used as is.

```python
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.named_commands import unix_word_rubout

bindings = KeyBindings()

@bindings.add("c-q")
def _(event):
    event.current_buffer.text = ""

@bindings.add("c-w")
def _(event):
    unix_word_rubout(event)

@bindings.add("c-x")
def _(event):
    event.current_buffer.insert_text("print(")
```

The `event` object provides access to the current buffer and the application:

| object                  | description                                                               |
|:------------------------|:--------------------------------------------------------------------------|
| `event.current_buffer`  | current input buffer (`text`, `insert_text()`, `delete()`, ...)           |
| `event.app`             | current prompt_toolkit application (`app.data` is the pyre `Data` object) |
| `event.key_sequence`    | the key sequence that triggered the binding                               |

The app mode is available as `event.app.mode`:

| mode           | description                |
|:---------------|:---------------------------|
| `"repl_cycle"` | main REPL prompt           |
| `"pyt++"`      | `_pyt++_` multiline editor |

This makes it possible to create a binding that works only in one of the modes:

```python
@bindings.add("c-x")
def _(event):
    if event.app.mode == "pyt++":
        event.current_buffer.insert_text("print()")
```

</details>

<details> <summary> notes </summary>

- Bindings are loaded once, when `pyre_bindings.py` is imported. Changes require restarting pyre; [\_._ settings_reload](../commands/shell_command.md) does not reload key bindings.
- Unlike regular prompt_toolkit applications, pyre does not create a separate `KeyBindings` object per mode, so a binding added to `bindings` is active everywhere unless it checks `event.app.mode`.
- The `_pyt++_` editor is created with the same `bindings` object in [pyre_commands.py](../../commands/pyt.py).

</details>

<details> <summary> read also </summary>

* [prompt toolkit KeyBindings](https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/key_bindings.html)
* [\_pyt++\_](../commands/pyt_pp.md)

</details>
