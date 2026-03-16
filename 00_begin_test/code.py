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

print("TEST_START: test_begin")

try:
    tcs = TCS3430(i2c)
    print("begin() result: true")
except (RuntimeError, OSError) as e:
    print(f"begin() result: false ({e})")
    print("TEST_FAIL: test_begin: begin() failed")
    print("~~END~~")
    raise SystemExit


chip_id = tcs.chip_id
print(f"Chip ID: 0x{chip_id:02X} (expected 0xDC)")
if chip_id != 0xDC:
    print(f"TEST_FAIL: test_begin: bad chip id 0x{chip_id:02X}")
    print("~~END~~")
    raise SystemExit

pon = tcs.power_on
print(f"PON status: {'true' if pon else 'false'}")
if not pon:
    print("TEST_FAIL: test_begin: PON not set")
    print("~~END~~")
    raise SystemExit

aen = tcs.als_enabled
print(f"AEN status: {'true' if aen else 'false'}")
if not aen:
    print("TEST_FAIL: test_begin: AEN not set")
    print("~~END~~")
    raise SystemExit

set_all(255, 255, 255)

tcs.als_gain = ALSGain.GAIN_64X
time.sleep(0.2)

x, y, z, ir1 = tcs.channels
print(f"Channels: X={x} Y={y} Z={z} IR1={ir1}")

if x == 0 or y == 0 or z == 0 or ir1 == 0:
    print(f"TEST_FAIL: test_begin: zero reading X={x} Y={y} Z={z} IR1={ir1}")
    print("~~END~~")
    raise SystemExit

# Second init should succeed
try:
    tcs2 = TCS3430(i2c)
    print("second begin() result: true")
except (RuntimeError, OSError):
    print("second begin() result: false")
    print("TEST_FAIL: test_begin: second begin failed")
    print("~~END~~")
    raise SystemExit

# Bad address should fail
try:
    tcs_bad = TCS3430(i2c, address=0x3A)
    print("bad address begin() result: true")
    print("TEST_FAIL: test_begin: bad address should fail")
    print("~~END~~")
    raise SystemExit
except (RuntimeError, OSError, ValueError):
    print("bad address begin() result: false")

set_all(0, 0, 0)
print("TEST_PASS: test_begin")

# End of file: print end marker for runner script
print("~~END~~")
