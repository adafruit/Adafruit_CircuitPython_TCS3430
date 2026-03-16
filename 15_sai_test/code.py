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


def wait_for_interrupt(tcs, timeout_s):
    start = time.monotonic()
    while (time.monotonic() - start) < timeout_s:
        if tcs.als_interrupt:
            return True
        time.sleep(0.001)
    return False


def read_z(tcs):
    _, _, z, _ = tcs.channels
    return z


i2c = board.I2C()

print("TEST_START: test_sai")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_sai: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)

tcs.integration_time = 50.0
tcs.als_gain = ALSGain.GAIN_16X
tcs.interrupt_persistence = InterruptPersistence.EVERY
tcs.interrupt_clear_on_read = False

set_all(255, 255, 255)
bright = read_average_z(tcs)

high = (bright // 2) if bright > 10 else (bright + 1)
tcs.als_threshold_low = 0
tcs.als_threshold_high = high

tcs.als_interrupt_enabled = True
tcs.sleep_after_interrupt = True
tcs.clear_als_interrupt()

set_all(255, 255, 255)
if not wait_for_interrupt(tcs, 2.0):
    print("TEST_FAIL: test_sai: interrupt timeout")
    print("~~END~~")
    raise SystemExit

z1 = read_z(tcs)
time.sleep(0.15)
z2 = read_z(tcs)

print(f"z1 (frozen): {z1}")
print(f"z2 (frozen): {z2}")
if z1 != z2:
    print("TEST_FAIL: test_sai: readings not frozen after interrupt")
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)
time.sleep(0.05)
tcs.als_threshold_low = 0
tcs.als_threshold_high = 0xFFFF
tcs.sleep_after_interrupt = False
tcs.clear_als_interrupt()
tcs.als_enabled = False
time.sleep(0.01)
tcs.als_enabled = True
time.sleep(0.4)

z3 = read_z(tcs)
set_all(255, 255, 255)
time.sleep(0.4)
z4 = read_z(tcs)

print(f"z3 (dark): {z3}")
print(f"z4 (bright): {z4}")

if z4 <= z3:
    print("TEST_FAIL: test_sai: readings did not update after clear")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_sai")

# End of file: print end marker for runner script
print("~~END~~")
