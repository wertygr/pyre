data.lexer:

type: `type[RegexLexer]`([pygments](https://pygments.org/))

The Pygments lexer class used for syntax highlighting. It defaults to `PythonLexer`:

```python
self.lexer: type[RegexLexer] = PythonLexer
```

The REPL passes the class itself to prompt_toolkit (`lexer=PygmentsLexer(data.lexer)`), for example in the command prompt and in the `_pyt++_` editor. To change the highlighting, assign another lexer class to `data.lexer` and rebuild [lexer_instance](lexer_instance.md) so that [pft](../pft.md) uses the same lexer.

<details> <summary> example </summary>

```python
from plugins.plugin_tools.plugin_types import (PluginApi, CommandContext)
from pygments.lexers import JsonLexer

def main(api: PluginApi, command_context: CommandContext, plugin_space: dict):
    data = api["data"]
    data.lexer = JsonLexer
    data.lexer_instance = data.lexer()
```

</details>

<details> <summary> read also </summary>

* [lexer_instance](lexer_instance.md)
* [pft](../pft.md)

</details>
