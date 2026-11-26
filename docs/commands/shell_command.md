commands table

| name                                   | require min argc |                               description |
|:---------------------------------------|------------------|------------------------------------------:|
| clear                                  | 2                |                             clear console |
| exit                                   | 2                |                                      exit |
| settings_reload                        | 2-3              |                 reread settings from disk |
| [run](shell_commands/run.md)           | 3                |                                run script |
| read_vf                                | 3                |                       read linecache file |
| unload_plug                            | 2                |             unloading plugins from memory |
| ls_vf                                  | 2                |                       list linecache file |
| del_vf                                 | 3                |                     delete linecache file |
| critical_error                         | 2                | artificial triggering of a critical error |
| [hook_run](shell_commands/hook_run.md) | 4                |                      artificial hook call |
| load_plug                              | 3                |                    artificial plugin call |
| ls_plug                                | 2                |                   view list loads plugins |
| [async start](../plugin/plugin_async.md) | 3              |        start async thread and event loop |
| [async run](../plugin/plugin_async.md)   | 4              |          start async_main of the plugin |
| [async del](../plugin/plugin_async.md)   | 4              |          cancel async plugin(s) |
| [async stop](../plugin/plugin_async.md)  | 3              |          cancel all, stop async thread |
| [async ls](../plugin/plugin_async.md)    | 3              |          view async thread and plugins |