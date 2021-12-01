import sys
import os
import time
import shutil
from typing import Optional, Iterable
from contextlib import contextmanager
import re
import json

import tests.data

DATA_DIR = tests.data.__path__[0]


def get_world_path(name: str) -> str:
    return os.path.join(DATA_DIR, "worlds_src", name)


def get_temp_world_path(name: str) -> str:
    return os.path.join(DATA_DIR, "worlds_temp", name)


def get_data_path(name: str) -> str:
    return os.path.join(DATA_DIR, "", name)


class BaseWorldTest:
    WorldPath = ""


def for_each_world(globals_, worlds: Iterable[str]):
    def wrap(cls: BaseWorldTest):
        for world in worlds:
            world_identifier = re.sub("\W|^(?=\d)", "_", world)
            globals_[world_identifier] = type(
                world_identifier, (cls,), {"WorldPath": world}
            )
        return None

    return wrap


class WorldTemp:
    def __init__(self, src_world_name: str, temp_world_name: Optional[str] = None):
        self._src_world_path = get_world_path(src_world_name)
        self._temp_world_path = get_temp_world_path(temp_world_name or src_world_name)
        self._metadata = None

    def __repr__(self):
        return f"WorldTemp({self.src_path}, {self.temp_path})"

    @property
    def src_path(self) -> str:
        return self._src_world_path

    @property
    def temp_path(self) -> str:
        return self._temp_world_path

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            with open(os.path.join(self.src_path, "world_test_data.json")) as f:
                self._metadata = json.load(f)
        return self._metadata

    def __enter__(self):
        clean_path(self._temp_world_path)
        create_temp_world(self.src_path, self.temp_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        clean_path(self.temp_path)


def clean_path(path: str):
    """Clean a given path removing all data at that path."""
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        os.remove(path)


def clean_temp_world(temp_world_name: str) -> str:
    """Remove the temporary world."""
    dst_path = get_temp_world_path(temp_world_name)
    clean_path(dst_path)
    return dst_path


def create_temp_world(
    src_world_name: str, temp_world_name: Optional[str] = None
) -> str:
    """Copy the world to a temporary location and return this path.

    :param src_world_name: The name of a world in ./worlds_src
    :param temp_world_name: Optional temporary name. Leave as None to auto to the same as src
    :return: The full path to a copy of the world
    """
    src_path = get_world_path(src_world_name)
    if temp_world_name is None:
        temp_world_name = src_world_name
    dst_path = clean_temp_world(temp_world_name)

    shutil.copytree(src_path, dst_path)
    return dst_path


@contextmanager
def timeout(test_instance, time_constraint: float, show_completion_time=False):
    start = time.time()
    yield

    end = time.time()
    delta = end - start
    if delta > time_constraint:
        test_instance.fail(
            f"Test execution didn't meet desired run time of {time_constraint}, ran in {delta} instead"
        )
    elif show_completion_time:
        print(
            f"Test ran in {delta} seconds, was required to run in {time_constraint} seconds",
            file=sys.stderr,
        )
