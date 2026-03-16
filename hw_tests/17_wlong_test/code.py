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


def ticks_us():
    """Return monotonic time in microseconds."""
    return time.monotonic_ns() // 1000


def read_average_z(tcs, samples=4):
    total = 0
    for _ in range(samples):
        _, _, z, _ = tcs.channels
        total += z
        time.sleep(0.02)
    return total // samples


def measure_interrupt_delay(tcs, timeout_us):
    start = ticks_us()
    while (ticks_us() - start) < timeout_us:
        if tcs.als_interrupt:
            return ticks_us() - start
        time.sleep(0.001)
    return 0


def measure_average_delay(tcs, samples, timeout_us):
    total = 0
    for _ in range(samples):
        tcs.clear_als_interrupt()
        delay_us = measure_interrupt_delay(tcs, timeout_us)
        if delay_us == 0:
            return 0
        total += delay_us
    return total // samples


i2c = board.I2C()

print("TEST_START: test_wlong")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_wlong: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(255, 255, 255)

tcs.integration_time = 2.78
tcs.als_gain = ALSGain.GAIN_16X
tcs.interrupt_clear_on_read = False
tcs.interrupt_persistence = InterruptPersistence.EVERY

bright = read_average_z(tcs)

high = (bright // 2) if bright > 10 else (bright + 1)
tcs.als_threshold_low = 0
tcs.als_threshold_high = high

tcs.als_interrupt_enabled = True
tcs.wait_enabled = True
tcs.wait_time = 2.78

tcs.wait_long = False

no_wlong = measure_average_delay(tcs, 5, 1000000)
if no_wlong == 0:
    print("TEST_FAIL: test_wlong: no-wlong timeout")
    print("~~END~~")
    raise SystemExit

tcs.wait_long = True

with_wlong = measure_average_delay(tcs, 5, 2000000)
if with_wlong == 0:
    print("TEST_FAIL: test_wlong: wlong timeout")
    print("~~END~~")
    raise SystemExit

print(f"No-WLONG delay us: {no_wlong}")
print(f"WLONG delay us: {with_wlong}")

if with_wlong < (no_wlong * 5):
    print("TEST_FAIL: test_wlong: WLONG did not extend delay")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_wlong")

# End of file: print end marker for runner script
print("~~END~~")
