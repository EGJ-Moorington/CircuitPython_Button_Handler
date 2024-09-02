# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board
from keypad import Keys

from button_handler import ButtonHandler, ButtonInitConfig, ButtonInput


def double_press_0():
    if button_1.is_pressed:
        double_press_0_holding_1()
        return
    print("Button 0 has been double pressed!")


def double_press_1():
    if button_0.is_pressed:
        double_press_1_holding_0()
        return
    print("Button 1 has been double pressed!")


def triple_press_0():
    if button_1.is_pressed:
        triple_press_0_holding_1()
        return
    print("Button 0 has been triple pressed!")


def triple_press_1():
    if button_0.is_pressed:
        triple_press_0_holding_1()
        return
    print("Button 1 has been triple pressed!")


def short_press_0():
    if button_1.is_pressed:
        short_press_0_holding_1()
        return
    print("Button 0 has been pressed quickly!")


def short_press_1():
    if button_0.is_pressed:
        short_press_1_holding_0()
        return
    print("Button 1 has been pressed quickly!")


def long_press_0():
    if button_1.is_pressed:
        long_press_0_holding_1()
        return
    print("Button 0 has been pressed for a long time!")


def long_press_1():
    if button_0.is_pressed:
        long_press_1_holding_0()
        return
    print("Button 1 has been pressed for a long time!")


def double_press_0_holding_1():
    print("Button 0 has been double pressed while button 1 was held down!")


def double_press_1_holding_0():
    print("Button 1 has been double pressed while button 0 was held down!")


def triple_press_0_holding_1():
    print("Button 0 has been triple pressed while button 1 was held down!")


def triple_press_1_holding_0():
    print("Button 1 has been triple pressed while button 0 was held down!")


def short_press_0_holding_1():
    print("Button 0 has been pressed quickly while button 1 was held down!")


def short_press_1_holding_0():
    print("Button 1 has been pressed quickly while button 0 was held down!")


def long_press_0_holding_1():
    print("Button 0 has been pressed for a long time while button 1 was held down!")


def long_press_1_holding_0():
    print("Button 1 has been pressed for a long time while button 0 was held down!")


config = ButtonInitConfig(max_multi_press=3)
scanner = Keys([board.D9, board.A2], value_when_pressed=False)
callback_inputs = {
    ButtonInput(ButtonInput.DOUBLE_PRESS, 0, double_press_0),
    ButtonInput(ButtonInput.DOUBLE_PRESS, 1, double_press_1),
    ButtonInput(3, 0, triple_press_0),
    ButtonInput(3, 1, triple_press_1),
    ButtonInput(ButtonInput.SHORT_PRESS, 0, short_press_0),
    ButtonInput(ButtonInput.SHORT_PRESS, 1, short_press_1),
    ButtonInput(ButtonInput.LONG_PRESS, 0, long_press_0),
    ButtonInput(ButtonInput.LONG_PRESS, 1, long_press_1),
}
button_handler = ButtonHandler(scanner.events, callback_inputs, 2, {0: config, 1: config})

button_0 = button_handler.buttons[0]
button_1 = button_handler.buttons[1]

while True:
    button_handler.update()
    time.sleep(0.0025)
