from itertools import repeat

import amulet.api.nbt as mcedit_nbt
import amulet.api.amulet_nbt as amulet_nbt
import time
import gc

FILEPATH = r"C:\Users\Ben\PycharmProjects\Unified-Minecraft-Editor\tests\worlds\1.13 World\level.dat"

mcedit_times = []
amulet_times = []

gc.disable()

for _ in repeat(None, 10000):
    start = time.time_ns()
    mcedit_nbt.load(FILEPATH)
    elapsed = time.time_ns() - start
    mcedit_times.append(elapsed)

gc.enable()
gc.collect()
gc.disable()

for _ in repeat(None, 10000):
    start = time.time_ns()
    amulet_nbt.load(FILEPATH)
    elapsed = time.time_ns() - start
    amulet_times.append(elapsed)

gc.enable()
gc.collect()

print(f"MCEdit: min = {min(mcedit_times) * 1e-9}, max = {max(mcedit_times) * 1e-9}, avg = {(sum(mcedit_times) / len(mcedit_times))  * 1e-9}")
print(f"Amulet: min = {min(amulet_times)  * 1e-9}, max = {max(amulet_times)  * 1e-9}, avg = {(sum(amulet_times) / len(amulet_times)) * 1e-9}")
