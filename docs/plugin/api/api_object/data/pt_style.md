data.pt_style:

type: `BaseStyle`([prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/styling.html))

The style used by the REPL for syntax highlighting. It is built during [settings_load](../settings_load.md) from `settings["color"]`:

```python
data.pt_style = style_from_pygments_dict({
    string_to_tokentype(key): value
    for key, value in settings["color"].items()
})
```

If the `color` section is invalid, the error is passed to [post](../post.md) and the style falls back to `Style([])`.

The style is passed to `prompt_toolkit` sessions (`style=data.pt_style`) and is used by [pft](../pft.md) when printing text.

<details> <summary> read also </summary>

* [settings](settings.md)
* [settings.md color](../../../../settings/settings.md)

</details>
