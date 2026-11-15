Command for manually working with the internal buffer.

<details> <summary> syntax </summary> 

```text
_._ buffer <mode> <text(optionally)>
 |     |     |             |- optional text
 |     |     |--------------- buffer mode
 |     |--------------------- subcommand
 |--------------------------- command 
```
</details>

<details> <summary> buffer modes </summary> 


| mode      | text is needed |             description |
|:----------|----------------|------------------------:|
| read      | False          |    read from the buffer |
| write     | True           |    write from the buffe |
| write_add | True           |  add text to the buffer |
| clean     | False          |   clear from the buffer |
</details>

<details> <summary> example </summary>

```pycon
>>> _pyt++_
1 |def test(a, b): return a + b
>>> _?_ test copy silent
>>> _._ buffer read
def test(a, b): return a + b
>>> _#_ settings["shlex"] == True = True
>>> _._ buffer write_add "# test function"
>>> _._ buffer read
def test(a, b): return a + b# test function
>>> _._ buffer write "5+5"
>>> _._ buffer read
5+5
>>> _._ buffer clean
>>> _._ buffer read

>>>
```
</details>

<details> <summary> read also </summary>

[buffer(plugin api)](../../plugin/api/api_object/buffer.md)
</details>