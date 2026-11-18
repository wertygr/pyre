data.argc:

type: `int`

The number of parsed arguments, i.e. `len(data.argv)`, including the command name itself. It is set by `dispatcher`:

```python
data.argc = len(data.argv)
```

It is passed to a plugin as `command_context["argc"]` and is used by the `require_args` decorator to check the minimum number of arguments.

<details> <summary> example </summary>

```pycon
>>> _example_plugin_ one two
```

inside the plugin `command_context["argc"] == 3` (command + two arguments).

</details>

<details> <summary> read also </summary>

* [argv](argv.md)
* [pars_command](../pars_command.md)

</details>
