data.postfix:

type: `str`

All arguments after the command name, joined by a single space. It is set by `dispatcher` before the command runs:

```python
data.postfix = " ".join(data.argv[1:])
```

It is used by the python execution commands (`_pyt_`, `_pyt-exec_`, `_pyt-eval_`) as the source code to execute, and it is also passed to a plugin as `command_context["postfix"]`.

Note: quoting and `shlex` rules are already applied to [argv](argv.md), so `postfix` is a plain space-joined string, not the original text.

<details> <summary> example </summary>

```pycon
>>> _example_plugin_ print("hello world")
```

inside the plugin `command_context["postfix"] == 'print("hello world")'`.

</details>

<details> <summary> read also </summary>

* [argv](argv.md)
* [pars_command](../pars_command.md)

</details>
