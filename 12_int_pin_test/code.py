# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# 12_int_pin_test: Verify physical INT pin toggles with ALS interrupts
# Breakout has open-drain inverter on INT: active-HIGH at MCU, needs pullup
import time

import board
import digitalio
import neopixel

from adafruit_tcs3430 import TCS3430, ALSGain, InterruptPersistence

PIXEL_COUNT = 5
INT_ACTIVE = True  # HIGH
INT_IDLE = False  # LOW

pixels = neopixel.NeoPixel(board.NEOPIXEL, PIXEL_COUNT, brightness=0.3)

int_pin = digitalio.DigitalInOut(board.D8)
int_pin.direction = digitalio.Direction.INPUT
int_pin.pull = digitalio.Pull.UP


def set_all(r, g, b):
    pixels.fill((r, g, b))
    time.sleep(0.2)


def wait_for_pin(expected, timeout_s):
    start = time.monotonic()
    while (time.monotonic() - start) < timeout_s:
        if int_pin.value == expected:
            return True
        time.sleep(0.001)
    return False


i2c = board.I2C()

print("TEST_START: 12_int_pin_test")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: 12_int_pin_test: begin() failed")
    print("~~END~~")
    raise SystemExit

set_all(0, 0, 0)

# Setup: fast integration, guaranteed-to-fire thresholds
tcs.integration_time = 2.78
tcs.als_gain = ALSGain.GAIN_4X
tcs.interrupt_persistence = InterruptPersistence.EVERY
tcs.interrupt_clear_on_read = False

# --- Step 1: Clear state, verify idle ---
tcs.als_enabled = False
tcs.als_interrupt_enabled = False
tcs.clear_als_interrupt()
time.sleep(0.05)

pin_state = int_pin.value
print(f"Idle pin: {'OK (idle)' if pin_state == INT_IDLE else 'UNEXPECTED'}")
if pin_state != INT_IDLE:
    print("TEST_FAIL: 12_int_pin_test: pin not idle at start")
    print("~~END~~")
    raise SystemExit

# --- Step 2: Enable ALS + AIEN with thresholds 0/0 (always fires) ---
tcs.als_threshold_low = 0
tcs.als_threshold_high = 0
tcs.clear_als_interrupt()
tcs.als_interrupt_enabled = True
tcs.als_enabled = True

if not wait_for_pin(INT_ACTIVE, 0.5):
    print("TEST_FAIL: 12_int_pin_test: INT never went active")
    print("~~END~~")
    raise SystemExit
print("INT went active: PASS")

# --- Step 3: Clear interrupt, verify pin returns to idle ---
tcs.als_enabled = False
tcs.clear_als_interrupt()
time.sleep(0.01)

if int_pin.value != INT_IDLE:
    print("TEST_FAIL: 12_int_pin_test: INT did not return to idle after clear")
    print("~~END~~")
    raise SystemExit
print("INT cleared to idle: PASS")

# --- Step 4: Verify INT stays idle with AIEN disabled ---
tcs.als_interrupt_enabled = False
tcs.clear_als_interrupt()
tcs.als_enabled = True
time.sleep(0.1)  # let several cycles run

if int_pin.value != INT_IDLE:
    print("TEST_FAIL: 12_int_pin_test: INT active with AIEN disabled")
    print("~~END~~")
    raise SystemExit
print("INT stays idle with AIEN off: PASS")

# --- Step 5: Toggle test - verify multiple assert/clear cycles ---
tcs.als_enabled = False
tcs.clear_als_interrupt()
tcs.als_interrupt_enabled = True
tcs.als_enabled = True

toggles = 0
for i in range(5):
    if not wait_for_pin(INT_ACTIVE, 0.2):
        break
    tcs.als_enabled = False
    tcs.clear_als_interrupt()
    if int_pin.value != INT_IDLE:
        break
    tcs.als_enabled = True
    toggles += 1

print(f"Toggle cycles: {toggles}/5")

if toggles < 5:
    print("TEST_FAIL: 12_int_pin_test: toggle cycles incomplete")
    print("~~END~~")
    raise SystemExit
print("Toggle test: PASS")

# Cleanup
tcs.als_interrupt_enabled = False
tcs.als_enabled = False
tcs.clear_als_interrupt()
set_all(0, 0, 0)

print("TEST_PASS: 12_int_pin_test")

# End of file: print end marker for runner script
print("~~END~~")
