`data` is the REPL state object. A single instance is created in [initialisation](../../../plugin_specification.md) and passed to every command, hook and [plugin](../../../plugin.md) function.

<details> <summary> fields </summary>

| name                                        | type             | short description                                                                                |
|:--------------------------------------------|:-----------------|:-------------------------------------------------------------------------------------------------|
| [repl_mode](repl_mode.md)                   | dict             | user namespace (globals or isolated locals)                                                      |
| [api](api.md)                               | PluginApi        | [plugins API](../../api.md) functions                                                            |
| [settings](settings.md)                     | dict             | loaded settings from `.pyre_settings.json`                                                       |
| [last_error](last_error.md)                 | str              | last error passed to [post](../post.md)                                                          |
| [pt_style](pt_style.md)                     | BaseStyle        | prompt_toolkit style built from `settings["color"]`                                              |
| [script_dir](script_dir.md)                 | str              | directory of the pyre kernel                                                                     |
| [plugin_space](plugin_space.md)             | dict             | shared storage for plugins                                                                       |
| [_local_repl_mode](_local_repl_mode.md)     | dict             | isolated namespace used when `settings["repl_mode"] == "locals"`                                 |
| [_pyt_plus_old_text](_pyt_plus_old_text.md) | str              | working text of the `_pyt++_` editor                                                             |
| [command](command.md)                       | str              | raw command line as it was entered                                                               |
| [postfix](postfix.md)                       | str              | all arguments after the command, joined by a space                                               |
| [argc](argc.md)                             | int              | number of arguments in [argv](argv.md)                                                           |
| [argv](argv.md)                             | list[str]        | parsed command arguments                                                                         |
| [lexer](lexer.md)                           | type[RegexLexer] | pygments lexer class used for highlighting                                                       |
| [lexer_instance](lexer_instance.md)         | RegexLexer       | lexer instance used by [pft](../pft.md)                                                          |
| [_repl_cache_id](_repl_cache_id.md)         | int              | counter of virtual source files registered by [register_repl_source](../register_repl_source.md) |
| [plugin_list](plugin_list.md)               | set[str]         | names of the currently loaded plugins                                                            |

</details>

<details> <summary> read also </summary>

* [plugins API](../../api.md)
* [plugin specification](../../../plugin_specification.md)

</details>
