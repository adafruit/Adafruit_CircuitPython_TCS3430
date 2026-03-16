# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel

from adafruit_tcs3430 import TCS3430, ALSGain, InterruptPersistence

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)


def set_all(r, g, b):
    pixels.fill((r, g, b))
    time.sleep(0.2)


def read_average_z(tcs, samples=4):
    total = 0
    for _ in range(samples):
        _, _, z, _ = tcs.channels
        total += z
        time.sleep(0.02)
    return total // samples


i2c = board.I2C()

print("TEST_START: test_thresholds")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_thresholds: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)

tcs.integration_time = 100.0
tcs.als_gain = ALSGain.GAIN_16X
tcs.interrupt_clear_on_read = False
tcs.interrupt_persistence = InterruptPersistence.CYCLES_1

dark = read_average_z(tcs)
print(f"Dark Z average: {dark}")

set_all(255, 255, 255)
bright = read_average_z(tcs)
print(f"Bright Z average: {bright}")
set_all(0, 0, 0)

low = dark + 20
high = (bright - 20) if bright > 20 else (bright // 2)
if high <= low:
    high = low + 10

print(f"Setting thresholds low={low} high={high}")

tcs.als_threshold_low = low
tcs.als_threshold_high = high

tcs.als_interrupt_enabled = True
print("ALS interrupt enabled")
tcs.clear_als_interrupt()

set_all(255, 255, 255)
start = time.monotonic()
while not tcs.als_interrupt and (time.monotonic() - start) < 2.0:
    time.sleep(0.01)
bright_int = tcs.als_interrupt
print(f"AINT after bright: {'true' if bright_int else 'false'}")
if not bright_int:
    print(f"TEST_FAIL: test_thresholds: AINT not set on bright, low={low} high={high}")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit

tcs.clear_als_interrupt()
set_all(0, 0, 0)
start = time.monotonic()
while not tcs.als_interrupt and (time.monotonic() - start) < 2.0:
    time.sleep(0.01)
dark_int = tcs.als_interrupt
print(f"AINT after dark: {'true' if dark_int else 'false'}")
if not dark_int:
    print("TEST_FAIL: test_thresholds: AINT not set on dark")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_thresholds")

# End of file: print end marker for runner script
print("~~END~~")
