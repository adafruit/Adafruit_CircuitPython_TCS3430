# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel

from adafruit_tcs3430 import TCS3430

PIXEL_COUNT = 5
pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)


def read_average(tcs, samples=5):
    sx, sy, sz, sir = 0, 0, 0, 0
    for _ in range(samples):
        x, y, z, ir1 = tcs.channels
        sx += x
        sy += y
        sz += z
        sir += ir1
        time.sleep(0.05)
    return sx // samples, sy // samples, sz // samples, sir // samples


i2c = board.I2C()

print("TEST_START: test_channels")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_channels: begin() failed")
    print("~~END~~")
    raise SystemExit

pixels.fill((255, 255, 255))
time.sleep(0.2)

x, y, z, ir1 = read_average(tcs)
print(f"Channel averages: X={x} Y={y} Z={z} IR1={ir1}")

if x == 0 or y == 0 or z == 0 or ir1 == 0:
    print(f"TEST_FAIL: test_channels: zero reading X={x} Y={y} Z={z} IR1={ir1}")
    print("~~END~~")
    raise SystemExit

pixels.fill((0, 0, 0))

print("All channels non-zero.")
print("TEST_PASS: test_channels")

# End of file: print end marker for runner script
print("~~END~~")
