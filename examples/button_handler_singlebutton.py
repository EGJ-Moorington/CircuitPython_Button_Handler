# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board
from keypad import Keys

from button_handler import ButtonHandler

scanner = Keys([board.D9], value_when_pressed=False)
button_handler = ButtonHandler(scanner.events)


def double_press():
    print("Double press detected!")


def short_press():
    print("Short press detected!")


def long_press():
    print("Long press detected!")


def hold():
    print("The button began being held down!")


actions = {
    "2_MULTI_PRESS": double_press,
    "SHORT_PRESS": short_press,
    "LONG_PRESS": long_press,
    "HOLD": hold,
}


def handle_input(input_):
    actions.get(input_.action, lambda: None)()


while True:
    inputs = button_handler.update()
    for input_ in inputs:
        handle_input(input_)
    time.sleep(0.0025)
