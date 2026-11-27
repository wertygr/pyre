from prompt_toolkit.document import Document

from pyre_core import Data, post
from pyre_pars_command import pars_command

from prompt_toolkit.completion import Completer, Completion, PathCompleter

class PathCompleterType: ...

PLUGINS_TREE = {
    '_._': {
        'settings_reload': PathCompleterType(),  # 'path' — подсказывать файлы
        'help': None,
    },
    '_ppm_': {
        'ls': None,
        'install': ['_ppm_', '_panel_', 'build'],
        'remove': ['_ppm_', '_panel_', 'build'],
    },
    '_panel_': {
        'start': None,
        'stop': None,
    },
    'build': {
        'run': PathCompleterType(),
    },
}

class CompleteState:
    def __init__(self, data: Data, document: Document, complete_event, path_complete) -> None:
        self.data = data
        self.document = document
        self.complete_event = complete_event
        self.path_completer = path_complete

class CommandCompletion(Completer):
    def __init__(self, data: Data, tree: dict) -> None:
        self.data = data
        self.tree = tree
        self.path_completer = PathCompleter()

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        commands = pars_command(self.data, False, text)
        trailing_space = text.endswith((" ", "\n", "\t", "\v")) or text == ''

        if not commands or (trailing_space and (not(len(commands[-1])) if len(commands) else False)):
            current_cmd = []
            current_word = ''
        else:
            current_cmd = list(commands[-1])

            if trailing_space:
                current_word = ''
            else:
                current_word = current_cmd.pop() if current_cmd else ''
        node = self.tree
        for token in current_cmd:
            if isinstance(node, dict) and token in node:
                node = node[token]
            else:
                if isinstance(node, dict):
                    return
                break

        if node is None:
            return

        if isinstance(node, dict):
            candidates = node.keys()
        elif isinstance(node, PathCompleterType):
            sub_doc = Document(text=current_word, cursor_position=len(current_word))
            yield from self.path_completer.get_completions(sub_doc, complete_event)
            return
        elif callable(node):
            try:
                candidates = node(current_word, current_cmd, document)
            except Exception as e:
                post(e, self.data)
                return

        elif isinstance(node, (list, tuple, set)):
            candidates = node

        else:
            return

        for item in candidates:
            if item.startswith(current_word):
                yield Completion(item, start_position=-len(current_word))