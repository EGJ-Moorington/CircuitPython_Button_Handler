# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board

from button_handler import ButtonHandler

button = ButtonHandler(board.D9)


def double_press():
    print("Double press detected!")


def short_press():
    print("Short press detected!")


def long_press():
    print("Long press detected!")


def holding():
    print("The button is being held down!")


actions = {
    "DOUBLE_PRESS": double_press,
    "SHORT_PRESS": short_press,
    "LONG_PRESS": long_press,
    "HOLDING": holding,
}


def handle_input(input_):
    actions.get(input_, lambda: None)()


while True:
    inputs = button.update()
    for input_ in inputs:
        handle_input(input_)
    time.sleep(0.0025)
