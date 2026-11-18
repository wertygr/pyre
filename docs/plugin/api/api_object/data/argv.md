data.argv:

type: `list[str]`

The parsed command arguments. `data.argv[0]` is the command name, the rest are its arguments.

The list is produced by `pars_command`:

- [command](command.md) is split with `shlex` (when `settings["shlex"]` is enabled) or with `str.split()`;
- global aliases are applied (when `settings["alias_globals"]` is enabled);
- the line is split into subcommands by `_&_` (when `settings["separator"]` is enabled);
- local aliases are applied (when `settings["alias_locals"]` is enabled).

Commands read their arguments from `data.argv`, and a plugin receives them as `command_context["argv"]`.

<details> <summary> example </summary>

```pycon
>>> _example_plugin_ one "two three"
```

inside the plugin `command_context["argv"] == ["_example_plugin_", "one", "two three"]`.

</details>

<details> <summary> read also </summary>

* [argc](argc.md)
* [postfix](postfix.md)
* [command](command.md)

</details>
