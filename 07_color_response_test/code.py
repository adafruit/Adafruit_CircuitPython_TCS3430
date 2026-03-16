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
    time.sleep(0.3)


def read_avg(tcs, samples=4):
    sx, sy, sz = 0, 0, 0
    for _ in range(samples):
        x, y, z, _ = tcs.channels
        sx += x
        sy += y
        sz += z
        time.sleep(0.03)
    return sx // samples, sy // samples, sz // samples


# Auto-gain: try gains from high to low until no channel exceeds 60000
GAINS = [ALSGain.GAIN_64X, ALSGain.GAIN_16X, ALSGain.GAIN_4X, ALSGain.GAIN_1X]


def auto_read(tcs):
    for g in GAINS:
        tcs.als_gain = g
        time.sleep(0.2)
        x, y, z = read_avg(tcs)
        if x < 60000 and y < 60000 and z < 60000:
            return x, y, z
    return x, y, z  # best effort at 1X


def dominant(target, other1, other2):
    if target == 0:
        return False
    if target * 5 < other1 * 4:
        return False
    if target * 5 < other2 * 4:
        return False
    return True


i2c = board.I2C()

print("TEST_START: 07_color_response_test")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: 07_color_response_test: begin() failed")
    print("~~END~~")
    raise SystemExit

tcs.integration_time = 50.0

failed = False

# Red: X should dominate
set_all(255, 0, 0)
x, y, z = auto_read(tcs)
print(f"  RED  X={x} Y={y} Z={z}")
if not dominant(x, y, z):
    print("TEST_FAIL: 07_color_response_test: red not dominant")
    failed = True

if not failed:
    # Green: Y should dominate
    set_all(0, 255, 0)
    x, y, z = auto_read(tcs)
    print(f"  GRN  X={x} Y={y} Z={z}")
    if not dominant(y, x, z):
        print("TEST_FAIL: 07_color_response_test: green not dominant")
        failed = True

if not failed:
    # Blue: Z should dominate
    set_all(0, 0, 255)
    x, y, z = auto_read(tcs)
    print(f"  BLU  X={x} Y={y} Z={z}")
    if not dominant(z, x, y):
        print("TEST_FAIL: 07_color_response_test: blue not dominant")
        failed = True

if not failed:
    # White: all non-zero
    set_all(255, 255, 255)
    x, y, z = auto_read(tcs)
    print(f"  WHT  X={x} Y={y} Z={z}")
    if x == 0 or y == 0 or z == 0:
        print("TEST_FAIL: 07_color_response_test: white has zero")
        failed = True

if not failed:
    print("TEST_PASS: 07_color_response_test")

set_all(0, 0, 0)

# End of file: print end marker for runner script
print("~~END~~")
