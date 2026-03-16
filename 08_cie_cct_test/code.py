# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import math
import time

import board
import neopixel

from adafruit_tcs3430 import TCS3430, ALSGain

PIXEL_COUNT = 5

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)


def set_all(r, g, b):
    pixels.fill((r, g, b))
    time.sleep(0.5)


def compute_cie(x_raw, y_raw, z_raw):
    """Compute CIE 1931 x, y chromaticity from raw X, Y, Z channels."""
    total = x_raw + y_raw + z_raw
    if total == 0:
        return None, None
    cie_x = x_raw / total
    cie_y = y_raw / total
    return cie_x, cie_y


def compute_cct(cie_x, cie_y):
    """Compute CCT using McCamy's approximation."""
    if cie_y == 0:
        return 0.0
    n = (cie_x - 0.3320) / (0.1858 - cie_y)
    cct = 449.0 * n * n * n + 3525.0 * n * n + 6823.3 * n + 5520.33
    return cct


i2c = board.I2C()

print("TEST_START: test_cie_cct")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_cie_cct: begin() failed")
    print("~~END~~")
    raise SystemExit

tcs.integration_time = 100.0
tcs.als_gain = ALSGain.GAIN_16X

set_all(255, 255, 255)

x, y, z, ir1 = tcs.channels
print(f"Raw channels: X={x} Y={y} Z={z} IR1={ir1}")

cie_x, cie_y = compute_cie(x, y, z)
if cie_x is None:
    print("TEST_FAIL: test_cie_cct: getCIE failed")
    set_all(0, 0, 0)
    print("~~END~~")
    raise SystemExit

cct = compute_cct(cie_x, cie_y)

print(f"CIE x,y: {cie_x:.4f}, {cie_y:.4f}")
print(f"CCT: {cct:.1f}")

set_all(0, 0, 0)

if cie_x <= 0.0 or cie_x >= 1.0 or cie_y <= 0.0 or cie_y >= 1.0:
    print(f"TEST_FAIL: test_cie_cct: CIE out of range x={cie_x:.4f} y={cie_y:.4f}")
    print("~~END~~")
    raise SystemExit

if cct < 2000.0 or cct > 10000.0:
    print(f"TEST_FAIL: test_cie_cct: CCT out of range {cct:.1f}")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_cie_cct")

# End of file: print end marker for runner script
print("~~END~~")
