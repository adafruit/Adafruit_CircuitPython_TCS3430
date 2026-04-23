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


def read_average_y(tcs, samples=4):
    sy = 0
    for _ in range(samples):
        _, y, _, _ = tcs.channels
        sy += y
        time.sleep(0.03)
    return sy // samples


i2c = board.I2C()

print("TEST_START: 14_persistence_test")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: 14_persistence_test: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)

tcs.integration_time = 50.0  # ~50ms per cycle
tcs.als_gain = ALSGain.GAIN_16X
tcs.interrupt_clear_on_read = False

# Calibrate: read dark and bright
dark = read_average_y(tcs)
print(f"  dark={dark}")

set_all(255, 255, 255)
bright = read_average_y(tcs)
print(f"  bright={bright}")

# Thresholds: window around dark so bright light is OUTSIDE
# low=0, high = dark + small margin -> bright readings exceed high -> fires
high = dark + (bright - dark) // 4
high = max(high, dark + 10)
tcs.als_threshold_low = 0
tcs.als_threshold_high = high
print(f"  threshold high={high}")

# Set persistence to 10 cycles
tcs.interrupt_persistence = InterruptPersistence.CYCLES_10
tcs.als_interrupt_enabled = True

# Clean start: disable ALS, clear, re-enable
set_all(0, 0, 0)
time.sleep(0.2)
tcs.als_enabled = False
tcs.clear_als_interrupt()
tcs.als_enabled = True

# Turn on light - should need 10 cycles (~500ms at 50ms/cycle) to fire
set_all(255, 255, 255)

# Check after 2 cycles (~100ms) - should NOT have fired yet
time.sleep(0.15)
tcs.als_enabled = False
early = tcs.als_interrupt
tcs.als_enabled = True
if early:
    print("TEST_FAIL: 14_persistence_test: interrupt fired too early")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit
print("  no interrupt after 150ms: OK")

# Wait for remaining cycles - should fire by ~600ms total
time.sleep(0.6)
if not tcs.als_interrupt:
    # Give extra time
    time.sleep(0.5)
    if not tcs.als_interrupt:
        print("TEST_FAIL: 14_persistence_test: interrupt did not fire")
        set_all(0, 0, 0)
        print("~~END~~")
        raise SystemExit
print("  interrupt fired after persistence: OK")

# Now test PERS_EVERY - should fire on first cycle
tcs.als_enabled = False
tcs.clear_als_interrupt()
tcs.interrupt_persistence = InterruptPersistence.EVERY
tcs.als_enabled = True

time.sleep(0.1)
if not tcs.als_interrupt:
    time.sleep(0.2)
    if not tcs.als_interrupt:
        print("TEST_FAIL: 14_persistence_test: PERS_EVERY did not fire")
        set_all(0, 0, 0)
        print("~~END~~")
        raise SystemExit
print("  PERS_EVERY fires immediately: OK")

set_all(0, 0, 0)
tcs.als_interrupt_enabled = False
print("TEST_PASS: 14_persistence_test")

# End of file: print end marker for runner script
print("~~END~~")
