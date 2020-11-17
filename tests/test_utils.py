import sys
import os
import time
import shutil
from contextlib import contextmanager

TESTS_DIR = os.path.dirname(__file__)


def get_world_path(name: str) -> str:
    return os.path.join(TESTS_DIR, "worlds", name)


def get_temp_world_path(name: str) -> str:
    return os.path.join(TESTS_DIR, "worlds_temp", name)


def create_temp_world(src_world_name: str) -> str:
    """Copy the world to a temporary location and return this path."""
    src_path = get_world_path(src_world_name)
    dst_path = get_temp_world_path(src_world_name)
    if os.path.isdir(dst_path):
        shutil.rmtree(dst_path)

    shutil.copytree(src_path, dst_path)
    return dst_path


def clean_temp_world(src_world_name: str):
    """Remove the temporary world."""
    dst_path = get_temp_world_path(src_world_name)
    if os.path.isdir(dst_path):
        shutil.rmtree(dst_path)
    elif os.path.isfile(dst_path):
        os.remove(dst_path)


def get_data_path(name: str) -> str:
    return os.path.join(TESTS_DIR, "data", name)


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
