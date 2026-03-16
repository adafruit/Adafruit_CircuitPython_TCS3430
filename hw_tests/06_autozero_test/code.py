# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board
import neopixel
import supervisor

from adafruit_tcs3430 import TCS3430, ALSGain

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.15)


def set_all(r, g, b):
    pixels.fill((r, g, b))
    time.sleep(0.2)


def ticks_us():
    """Return monotonic time in microseconds."""
    return supervisor.ticks_ms() * 1000


def wait_for_reading(tcs, timeout_us):
    """Poll channels until any is non-zero. Returns elapsed microseconds or None."""
    start = ticks_us()
    while (ticks_us() - start) < timeout_us:
        x, y, z, ir1 = tcs.channels
        if x > 0 or y > 0 or z > 0 or ir1 > 0:
            return ticks_us() - start
        time.sleep(0.005)
    return None


def power_cycle(tcs):
    tcs.power_on = False
    time.sleep(0.05)
    tcs.power_on = True
    tcs.als_enabled = True
    time.sleep(0.05)


i2c = board.I2C()

print("TEST_START: test_autozero")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_autozero: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(20, 20, 20)

tcs.integration_time = 100.0
tcs.als_gain = ALSGain.GAIN_16X

# Enable autozero
tcs.auto_zero_mode = True
tcs.auto_zero_nth = 0x7F

power_cycle(tcs)

az_time = wait_for_reading(tcs, 2000000)
if az_time is None:
    print("TEST_FAIL: test_autozero: autozero read failed")
    print("~~END~~")
    raise SystemExit

# Disable autozero
tcs.auto_zero_mode = False
tcs.auto_zero_nth = 0

power_cycle(tcs)

no_az_time = wait_for_reading(tcs, 2000000)
if no_az_time is None:
    print("TEST_FAIL: test_autozero: no-az read failed")
    print("~~END~~")
    raise SystemExit

print(f"Autozero first-read us: {az_time}")
print(f"No-auto-zero first-read us: {no_az_time}")

if abs(az_time - no_az_time) < 1000:
    print("NOTE: test_autozero timing delta subtle; readings valid")

if tcs.auto_zero_mode or tcs.auto_zero_nth != 0:
    print("TEST_FAIL: test_autozero: config readback mismatch")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_autozero")

# End of file: print end marker for runner script
print("~~END~~")
