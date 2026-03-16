# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel

from adafruit_tcs3430 import TCS3430, ALSGain

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)


def set_all(r, g, b):
    pixels.fill((r, g, b))
    time.sleep(0.5)


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

print("TEST_START: test_power")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_power: begin() failed")
    print("~~END~~")
    raise SystemExit

print("Powering off sensor")
tcs.power_on = False
print(f"isPoweredOn after off: {'true' if tcs.power_on else 'false'}")
time.sleep(0.05)

x, y, z, ir1 = read_average(tcs)
print(f"Read while off: X={x} Y={y} Z={z} IR1={ir1}")
if x != 0 or y != 0 or z != 0 or ir1 != 0:
    print(f"TEST_FAIL: test_power: non-zero while off X={x} Y={y} Z={z} IR1={ir1}")
    print("~~END~~")
    raise SystemExit

print("Powering on sensor + enabling ALS")
tcs.power_on = True
tcs.als_enabled = True
print(f"isPoweredOn after on: {'true' if tcs.power_on else 'false'}")

tcs.integration_time = 100.0
tcs.als_gain = ALSGain.GAIN_16X

set_all(255, 255, 255)

x, y, z, ir1 = read_average(tcs)
print(f"Read after on: X={x} Y={y} Z={z} IR1={ir1}")

set_all(0, 0, 0)

if x == 0 or y == 0 or z == 0 or ir1 == 0:
    print(f"TEST_FAIL: test_power: zero after power on X={x} Y={y} Z={z} IR1={ir1}")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_power")

# End of file: print end marker for runner script
print("~~END~~")
