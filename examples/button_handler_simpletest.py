# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board
from keypad import Keys

from button_handler import ButtonHandler

scanner = Keys([board.D9], value_when_pressed=False)
button_handler = ButtonHandler(scanner.events, set())

while True:
    inputs = button_handler.update()
    for input_ in inputs:
        print(input_)
    time.sleep(0.01)
