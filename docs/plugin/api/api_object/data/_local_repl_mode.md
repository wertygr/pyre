data._local_repl_mode:

type: `dict`

An isolated namespace (internal, starts with `_`). When `settings["repl_mode"] == "locals"`, [settings_load](../settings_load.md) makes [repl_mode](repl_mode.md) point to this dictionary:

```python
if settings["repl_mode"] == "globals":
    data.repl_mode = globals()
    data.repl_mode["data"] = data
else:
    data.repl_mode = data._local_repl_mode
```

Thus the user code always executes in `data.repl_mode`, and the kernel namespace stays clean in the default `locals` mode. Plugins should use [repl_mode](repl_mode.md) instead of this field.

<details> <summary> read also </summary>

* [repl_mode](repl_mode.md)
* [settings.md repl_mode](../../../../settings/settings.md)

</details>
