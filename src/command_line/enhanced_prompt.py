from __future__ import annotations

import shlex
from typing import List, Dict, Union, Callable, Generator

from prompt_toolkit import PromptSession, HTML, print_formatted_text
from prompt_toolkit.completion import Completion, Completer, ThreadedCompleter
from prompt_toolkit.shortcuts import ProgressBar


def exit_completer(parts: List[str]) -> Completion:
    if len(parts) == 1:
        yield Completion("-f", start_position=0)

    elif len(parts) == 2:
        if parts[1] == "-f":
            yield Completion("", start_position=0)

        else:
            yield Completion("-f", start_position=-len(parts[1]) + 1)


class _CommandCompleter(Completer):

    def __init__(self, *args, **kwargs):
        super(_CommandCompleter, self).__init__(*args, **kwargs)
        self._completion_map: Dict[str, Union[Callable, Generator]] = {
            "exit": exit_completer, "help": None
        }

    def add_command(
        self, command_name: str, completion_callable: Callable[[List[str]], Completion]
    ):
        if command_name not in self._completion_map:
            self._completion_map[command_name] = completion_callable

    def get_completions(self, document, complete_event):
        for cmd in self._completion_map.keys():
            text = document.text

            try:
                parts = shlex.split(text)
            except ValueError:
                return Completion('"', start_position=0)

            if text.endswith(" "):
                parts.append(" ")
            if not parts:
                yield Completion(cmd, start_position=-len(text))

            elif cmd.startswith(parts[0]):
                if len(parts) == 1 and not text.endswith(" "):
                    yield Completion(cmd, start_position=-len(text))

                elif callable(self._completion_map[cmd]):
                    yield from self._completion_map[cmd](parts)


class EnhancedPromptIO:

    def __init__(self):
        self._completer = _CommandCompleter()

        self._session = PromptSession(completer=ThreadedCompleter(self._completer))

    def print(self, *args, **kwargs):
        if len(args) >= 1:
            message = args[0]
        else:
            message = ""

        if "color" in kwargs:
            message = HTML(f"<{kwargs['color']}>{message}</{kwargs['color']}>")
        print_formatted_text(message)

    def progress_bar(self, *args, **kwargs):
        return ProgressBar(*args, **kwargs)

    @property
    def completer(self):
        return self._completer

    @completer.setter
    def completer(self, obj):
        self._completer = obj

    def get_input(self, prompt_message: str) -> str:
        try:
            return self._session.prompt(prompt_message)

        except KeyboardInterrupt:
            return "exit -f"
