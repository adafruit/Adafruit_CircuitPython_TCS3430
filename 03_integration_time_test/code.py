# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel

from adafruit_tcs3430 import TCS3430, ALSGain

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)


def read_average_y(tcs, samples=5):
    sy = 0
    for _ in range(samples):
        _, y, _, _ = tcs.channels
        sy += y
        time.sleep(0.05)
    return sy // samples


i2c = board.I2C()

print("TEST_START: test_integration_time")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_integration_time: begin() failed")
    print("~~END~~")
    raise SystemExit

tcs.als_gain = ALSGain.GAIN_16X

pixels.fill((255, 255, 255))
time.sleep(0.5)

tcs.integration_time = 20.0
print("Integration time set to 20 ms")
time.sleep(0.03)
y_short = read_average_y(tcs)
print(f"Y average (20 ms): {y_short}")

tcs.integration_time = 200.0
print("Integration time set to 200 ms")
time.sleep(0.22)
y_long = read_average_y(tcs)
print(f"Y average (200 ms): {y_long}")

pixels.fill((0, 0, 0))

if y_long <= y_short:
    print(f"TEST_FAIL: test_integration_time: long<=short {y_long} <= {y_short}")
    print("~~END~~")
    raise SystemExit

print("Longer integration produced higher Y as expected.")
print("TEST_PASS: test_integration_time")

# End of file: print end marker for runner script
print("~~END~~")
