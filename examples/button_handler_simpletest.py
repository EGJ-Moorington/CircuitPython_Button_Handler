# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board

from button_handler import ButtonHandler

button = ButtonHandler(board.D9)

while True:
    button.update()
    print(button.is_pressed)
    time.sleep(0.01)
