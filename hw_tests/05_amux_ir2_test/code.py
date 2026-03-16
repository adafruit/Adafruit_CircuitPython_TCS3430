# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time

import board

from adafruit_tcs3430 import TCS3430

i2c = board.I2C()

print("TEST_START: test_amux_ir2")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: test_amux_ir2: begin() failed")
    print("~~END~~")
    raise SystemExit

print("Setting AMUX to X (IR2 disabled)")
tcs.als_mux_ir2 = False

x, y, z, ir1 = tcs.channels
print(f"AMUX off (X channel): X={x} Y={y} Z={z} IR1={ir1}")

print("Setting AMUX to IR2")
tcs.als_mux_ir2 = True

time.sleep(tcs.integration_time / 1000.0)
ir2 = tcs.ir2
print(f"AMUX on (IR2): IR2={ir2}")

tcs.als_mux_ir2 = False

diff = abs(ir2 - x)
print(f"Difference between X and IR2: {diff}")

if x == 0 or ir2 == 0:
    print(f"TEST_FAIL: test_amux_ir2: zero X/IR2 X={x} IR2={ir2}")
    print("~~END~~")
    raise SystemExit

print("TEST_PASS: test_amux_ir2")

# End of file: print end marker for runner script
print("~~END~~")
