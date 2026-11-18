data._repl_cache_id:

type: `int`

An internal counter (starts with `_`) of the virtual source files registered by [register_repl_source](../register_repl_source.md). Each call increments it and creates a new unique file name in [linecache](https://docs.python.org/3/library/linecache.html):

```python
data._repl_cache_id += 1
filename = f"<py_repl_{data._repl_cache_id}>"
linecache.cache[filename] = (len(source), None, source.splitlines(keepends=True), filename)
```

Such virtual files make dynamically executed code available for [introspection](../../../../commands/source_code.md) and tracebacks. Plugins should use [register_repl_source](../register_repl_source.md) instead of changing this field.

<details> <summary> read also </summary>

* [register_repl_source](../register_repl_source.md)
* [repl_mode](repl_mode.md)

</details>
