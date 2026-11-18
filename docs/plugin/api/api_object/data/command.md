data.command:

type: `str`

The raw command line exactly as the user typed it, before parsing. It is set in the REPL loop:

```python
data.command = session.prompt(...)
pars_command(data)
```

It is also set by shell commands that re-inject a command line (for example `_._ run` in the [internal buffer](../../../../commands/shell_commands/run.md)).

[pars_command](../pars_command.md) converts `data.command` into [argv](argv.md).

<details> <summary> example </summary>

```pycon
>>> _example_plugin_ 1 2 3
```

inside the plugin `data.command == "_example_plugin_ 1 2 3"`.

</details>

<details> <summary> read also </summary>

* [argv](argv.md)
* [pars_command](../pars_command.md)

</details>
