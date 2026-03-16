# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel
import supervisor

from adafruit_tcs3430 import TCS3430, ALSGain

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)


def set_all(r, g, b):
    pixels.fill((r, g, b))
    time.sleep(0.2)


def ticks_us():
    """Return monotonic time in microseconds."""
    return supervisor.ticks_ms() * 1000


def measure_cycle_period(tcs, cycles, timeout_us):
    """Measure cycle-to-cycle period using interrupt_clear_on_read.
    Returns average of N consecutive cycle periods in microseconds.
    """
    tcs.interrupt_clear_on_read = True

    # Wait for first AINT (and auto-clear it by reading)
    t = ticks_us()
    while (ticks_us() - t) < timeout_us:
        if tcs.als_interrupt:
            break
        time.sleep(0.0001)

    # Now measure N consecutive cycles
    total = 0
    for _ in range(cycles):
        start = ticks_us()
        while (ticks_us() - start) < timeout_us:
            if tcs.als_interrupt:
                total += ticks_us() - start
                break
            time.sleep(0.0001)
    return total // cycles


i2c = board.I2C()

print("TEST_START: test_wait")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_wait: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(255, 255, 255)

tcs.integration_time = 50.0
tcs.als_gain = ALSGain.GAIN_16X

# Measure without wait (average of 4 cycles)
tcs.wait_enabled = False
no_wait = measure_cycle_period(tcs, 4, 1500000)

# Measure with wait — 100ms wait time (average of 4 cycles)
tcs.wait_enabled = True
tcs.wait_time = 100.0
with_wait = measure_cycle_period(tcs, 4, 1500000)

print(f"No-wait avg us: {no_wait}")
print(f"With-wait avg us: {with_wait}")

# With-wait should be at least 50ms longer
if with_wait <= (no_wait + 50000):
    print("TEST_FAIL: test_wait: wait did not extend cycle")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)
print("TEST_PASS: test_wait")

# End of file: print end marker for runner script
print("~~END~~")
