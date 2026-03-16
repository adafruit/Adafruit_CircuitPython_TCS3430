# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel

from adafruit_tcs3430 import TCS3430, ALSGain

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=1.0)


def set_all(r, g, b):
    pixels.fill((r, g, b))


i2c = board.I2C()

print("TEST_START: 09_saturation_test")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: 09_saturation_test: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(255, 255, 255)

print("Settings: gain=128X, integration=711 ms, brightness=255")
tcs.als_gain = ALSGain.GAIN_128X
# Max integration time: ATIME=255 -> 711ms
tcs.integration_time = 711.0
tcs.clear_als_saturated()
time.sleep(0.8)  # wait for full integration cycle

# Check multiple times - ASAT may take a cycle to latch
saturated = False
tries = 0
for i in range(5):
    tries = i + 1
    if tcs.als_saturated:
        saturated = True
        break
    time.sleep(0.3)

if not saturated:
    print("TEST_FAIL: 09_saturation_test: ASAT not set")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit

print(f"ASAT detected after {tries} checks")

set_all(0, 0, 0)
print("TEST_PASS: 09_saturation_test")

# End of file: print end marker for runner script
print("~~END~~")
