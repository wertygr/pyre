data.lexer_instance:

type: `RegexLexer`([pygments](https://pygments.org/))

An instance of [lexer](lexer.md), created once in the `Data` constructor:

```python
self.lexer_instance: RegexLexer = self.lexer()
```

[pft](../pft.md) uses it to tokenize the text before printing:

```python
tokens = list(data.lexer_instance.get_tokens(str(text)))
```

If you change [lexer](lexer.md), recreate the instance (`data.lexer_instance = data.lexer()`) so that printed output uses the new lexer.

<details> <summary> read also </summary>

* [lexer](lexer.md)
* [pft](../pft.md)

</details>
