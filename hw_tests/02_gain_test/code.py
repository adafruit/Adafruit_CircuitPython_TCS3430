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


def read_average_y(tcs, samples=4):
    sy = 0
    for _ in range(samples):
        _, y, _, _ = tcs.channels
        sy += y
        time.sleep(0.03)
    return sy // samples


i2c = board.I2C()

print("TEST_START: 02_gain_test")

try:
    tcs = TCS3430(i2c)
except (RuntimeError, OSError):
    print("TEST_FAIL: 02_gain_test: begin() failed")
    print("~~END~~")
    raise SystemExit

tcs.integration_time = 50.0
tcs.als_gain = ALSGain.GAIN_1X

# Auto-calibrate: find brightness where 1X reads 50-200
brightness = 5
y1x = 0
for attempt in range(20):
    pixels.brightness = brightness / 255.0
    set_all(255, 255, 255)
    time.sleep(0.2)
    y1x = read_average_y(tcs)
    print(f"  cal: bright={brightness} Y@1X={y1x}")
    if 50 <= y1x <= 200:
        break
    if y1x < 50:
        brightness = brightness + 10 if brightness < 200 else 255
    else:
        brightness = brightness - 5 if brightness > 10 else 1
    if attempt == 19:
        print("  cal: using best effort")

# Step through gains
gains = [ALSGain.GAIN_1X, ALSGain.GAIN_4X, ALSGain.GAIN_16X, ALSGain.GAIN_64X, ALSGain.GAIN_128X]
prev = 0
for i, gain in enumerate(gains):
    tcs.als_gain = gain
    time.sleep(0.15)
    y = read_average_y(tcs)
    print(f"  gain_step={i} Y={y}")
    if i > 0 and prev < 60000 and y <= prev:
        print(f"TEST_FAIL: 02_gain_test: not increasing prev={prev} curr={y}")
        set_all(0, 0, 0)
        print("~~END~~")
        raise SystemExit
    prev = y

set_all(0, 0, 0)
print("TEST_PASS: 02_gain_test")

# End of file: print end marker for runner script
print("~~END~~")
