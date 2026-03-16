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
    time.sleep(0.2)


i2c = board.I2C()

print("TEST_START: test_int_read_clear")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_int_read_clear: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(255, 255, 255)

tcs.integration_time = 50.0
tcs.als_gain = ALSGain.GAIN_16X

# Wait for a cycle to complete so AINT sets
time.sleep(0.2)

# Phase 1: INT_READ_CLEAR off — AINT should persist across reads
tcs.interrupt_clear_on_read = False

# Disable ALS so no new cycles interfere, then clear
tcs.als_enabled = False
tcs.clear_als_interrupt()
# Re-enable and wait for one cycle
tcs.als_enabled = True
time.sleep(0.2)

read1 = tcs.als_interrupt
read2 = tcs.als_interrupt
read3 = tcs.als_interrupt

if not read1 or not read2 or not read3:
    print(f"TEST_FAIL: test_int_read_clear: AINT not persistent r1={read1} r2={read2} r3={read3}")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit
print("  Phase 1 OK: AINT persists across 3 reads")

# Phase 2: INT_READ_CLEAR on — first read sees AINT, second should not
tcs.interrupt_clear_on_read = True

# Stop ALS, clear, restart, wait for one cycle
tcs.als_enabled = False
tcs.clear_als_interrupt()
tcs.als_enabled = True
time.sleep(0.2)

first_read = tcs.als_interrupt
# Immediately read again — should be cleared by first read
second_read = tcs.als_interrupt

if not first_read:
    print("TEST_FAIL: test_int_read_clear: AINT not set on first read")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit
if second_read:
    print("TEST_FAIL: test_int_read_clear: AINT not auto-cleared on read")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit
print("  Phase 2 OK: AINT auto-cleared on read")

set_all(0, 0, 0)
print("TEST_PASS: test_int_read_clear")

# End of file: print end marker for runner script
print("~~END~~")
