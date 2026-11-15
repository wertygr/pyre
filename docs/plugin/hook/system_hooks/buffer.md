This hook is called when working with the buffer before changes are made to the buffer itself if use_hook = True

<details> <summary> hook format </summary>

```python
hook_parameter = {
    "mode": "read", # type str("write"/"write_add"/"read")
    "text": ""      # type str
}
```
</details>

<details> <summary> read also </summary> 

[buffer(plugins api)](../../api/api_object/buffer.md)
</details>