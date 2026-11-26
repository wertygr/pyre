Checks `argc` before running a [shell command](../../commands/shell_command.md) or a wrapped plugin function.

<details> <summary> signature </summary>

```python
def require_args(min_argc: int) -> Callable[[CommandFunc], CommandFunc]:
    ...
```

| parametr  | description                                   |
|:----------|-----------------------------------------------|
| min_argc  | minimal `argc` including the command itself   |

The decorator prints `[<function name>]: not enough arguments(min argc: N)` and does not call the wrapped function when `argc < min_argc`.

</details>

<details> <summary> example </summary>

```python
from pyre_core import require_args, Data

@require_args(3)
def my_command(data: Data):
    # here argc >= 3 is guaranteed
    ...
```

```pycon
>>> _._ my_command
[my_command]: not enough arguments(min argc: 3)
```

</details>

<details> <summary> read also </summary>

* [plugins API](api.md)
* [plugin command context](../plugin_command_context.md)

</details>
