from contextlib import ContextDecorator

class FakeCompleter:

    def add_command(self, *args, **kwargs):
        pass

class FakeProgressBar(ContextDecorator):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __call__(self, iterable):
        yield from iter(iterable)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ReducedPromptIO:

    def __init__(self):
        self._completer = FakeCompleter()

    def print(self, *args, **kwargs):
        if "color" in kwargs:
            del  kwargs["color"]

        print(*args, **kwargs)

    def progress_bar(self, *args, **kwargs):
        return FakeProgressBar(*args, **kwargs)

    @property
    def completer(self):
        return self._completer

    @completer.setter
    def completer(self, obj):
        self._completer = obj

    def get_input(self, prompt_message: str) -> str:
        return input(prompt_message)
