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


i2c = board.I2C()

print("TEST_START: test_interrupts")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_interrupts: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)

tcs.integration_time = 100.0
tcs.als_gain = ALSGain.GAIN_16X
# Set high threshold low so bright light exceeds it and triggers AINT
tcs.als_threshold_low = 0
tcs.als_threshold_high = 100
tcs.interrupt_clear_on_read = False
print("Enabling ALS interrupt (AIEN)")
tcs.als_interrupt_enabled = True
tcs.clear_als_interrupt()

print(f"AINT status before light: {'true' if tcs.als_interrupt else 'false'}")

set_all(255, 255, 255)

# Poll for interrupt
int_fired = False
for i in range(20):
    time.sleep(0.1)
    aint = tcs.als_interrupt
    print(f"Poll {i} AINT={'true' if aint else 'false'}")
    if aint:
        int_fired = True
        break

if not int_fired:
    print("TEST_FAIL: test_interrupts: ALS interrupt never fired (2s timeout)")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit

print("Clearing ALS interrupt")
tcs.clear_als_interrupt()
print(f"AINT status after clear: {'true' if tcs.als_interrupt else 'false'}")

print("Disabling ALS interrupt (AIEN)")
tcs.als_interrupt_enabled = False

set_all(0, 0, 0)
print("TEST_PASS: test_interrupts")

# End of file: print end marker for runner script
print("~~END~~")
