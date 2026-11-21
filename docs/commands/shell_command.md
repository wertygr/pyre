commands table

| name                                   | require min argc |                               description |
|:---------------------------------------|------------------|------------------------------------------:|
| clear                                  | 2                |                             clear console |
| exit                                   | 2                |                                      exit |
| settings_reload                        | 2-3              |                 reread settings from disk |
| [run](shell_commands/run.md)           | 3                |                                run script |
| read_vf                                | 3                |                       read linecache file |
| unload_plugin                          | 2                |             unloading plugins from memory |
| ls_vf                                  | 2                |                       list linecache file |
| del_vf                                 | 3                |                     delete linecache file |
| critical_error                         | 2                | artificial triggering of a critical error |
| [hook_run](shell_commands/hook_run.md) | 4                |                      artificial hook call |
| load_plugin                            | 3                |                    artificial plugin call |
| ls_plug                                | 2                |                   view list loads plugins |
| [async_start](../plugin/plugin_async.md) | 2              |        start async thread and event loop |
| [async_run](../plugin/plugin_async.md)   | 3              |          start async_main of the plugin |
| [async_del](../plugin/plugin_async.md)   | 3              |          cancel async plugin(s) |
| [async_stop](../plugin/plugin_async.md)  | 2              |          cancel all, stop async thread |
| [async_ls](../plugin/plugin_async.md)    | 2              |          view async thread and plugins |