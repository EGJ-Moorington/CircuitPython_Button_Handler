# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board
from keypad import Keys

from button_handler import ButtonHandler, ButtonInitConfig, ButtonInput


def double_press():
    print("Double press detected!")


def short_press():
    print("Short press detected!")


def long_press():
    print("Long press detected!")


def hold():
    print("The button began being held down!")


actions = {
    ButtonInput(ButtonInput.DOUBLE_PRESS, callback=double_press),
    ButtonInput(ButtonInput.SHORT_PRESS, callback=short_press),
    ButtonInput(ButtonInput.LONG_PRESS, callback=long_press),
    ButtonInput(ButtonInput.HOLD, callback=hold),
}

scanner = Keys([board.D9], value_when_pressed=False)
button_handler = ButtonHandler(scanner.events, actions)


while True:
    button_handler.update()
    time.sleep(0.0025)
