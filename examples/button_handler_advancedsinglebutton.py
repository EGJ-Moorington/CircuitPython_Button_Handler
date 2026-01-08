# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2026 EGJ Moorington
# SPDX-FileCopyrightText: Copyright (c) 2026 George Hartzell
#
# SPDX-License-Identifier: Unlicense

#
# Demonstrates:
# - handling a triple press
# - setting configurations for buttons (e.g. multi_press_interval)
#

import time

import board
from keypad import Keys

from button_handler import ButtonHandler, ButtonInitConfig, ButtonInput


def double_press():
    print("Double press detected!")


def triple_press():
    print("Triple press detected!")


def short_press():
    print("Short press detected!")


def long_press():
    print("Long press detected!")


def hold():
    print("The button began being held down!")


callback_inputs = {
    ButtonInput(ButtonInput.DOUBLE_PRESS, 0, double_press),
    ButtonInput(3, 0, triple_press),
    ButtonInput(ButtonInput.SHORT_PRESS, 0, short_press),
    ButtonInput(ButtonInput.LONG_PRESS, 0, long_press),
    ButtonInput(ButtonInput.HOLD, 0, hold),
}


config = ButtonInitConfig(multi_press_interval=500, max_multi_press=3)
scanner = Keys((board.D9,), value_when_pressed=False, pull=True)
button_handler = ButtonHandler(scanner.events, callback_inputs, 1, {0: config})


while True:
    button_handler.update()
    time.sleep(0.0025)
