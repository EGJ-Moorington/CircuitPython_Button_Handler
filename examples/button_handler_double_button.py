# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

"""
This example demonstrates simple usage of the library for a two button set-up.
"""

import time

import board
from keypad import Keys

from button_handler import ButtonHandler, ButtonInput


def double_press_0():
    print("Button 0 has been double pressed!")


def double_press_1():
    print("Button 1 has been double pressed!")


def short_press_0():
    print("Button 0 has been pressed quickly!")


def short_press_1():
    print("Button 1 has been pressed quickly!")


def long_press_0():
    print("Button 0 has been pressed for a long time!")


def long_press_1():
    print("Button 1 has been pressed for a long time!")


scanner = Keys([board.D9, board.A2], value_when_pressed=False)
callback_inputs = {
    ButtonInput(ButtonInput.DOUBLE_PRESS, 0, double_press_0),
    ButtonInput(ButtonInput.DOUBLE_PRESS, 1, double_press_1),
    ButtonInput(ButtonInput.SHORT_PRESS, 0, short_press_0),
    ButtonInput(ButtonInput.SHORT_PRESS, 1, short_press_1),
    ButtonInput(ButtonInput.LONG_PRESS, 0, long_press_0),
    ButtonInput(ButtonInput.LONG_PRESS, 1, long_press_1),
}

button_handler = ButtonHandler(scanner.events, callback_inputs, 2)

while True:
    button_handler.update()
    time.sleep(0.0025)
