# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: Unlicense

import time

import board

from button_handler import ButtonHandler

button_a = ButtonHandler(board.D9)
button_b = ButtonHandler(board.A2)


def double_press_a():
    print("Button A has been double pressed!")


def double_press_b():
    print("Button B has been double pressed!")


def short_press_a():
    print("Button A has been pressed quickly!")


def short_press_b():
    print("Button B has been pressed quickly!")


def long_press_a():
    print("Button A has been pressed for a long time!")


def long_press_b():
    print("Button B has been pressed for a long time!")


def double_press_a_holding_b():
    print("Button A has been double pressed while button B was held down!")


def double_press_b_holding_a():
    print("Button B has been double pressed while button A was held down!")


def short_press_a_holding_b():
    print("Button A has been pressed quickly while button B was held down!")


def short_press_b_holding_a():
    print("Button B has been pressed quickly while button A was held down!")


def long_press_a_holding_b():
    print("Button A has been pressed for a long time while button B was held down!")


def long_press_b_holding_a():
    print("Button B has been pressed for a long time while button A was held down!")


actions = {
    ("DOUBLE_PRESS", "A"): double_press_a,
    ("DOUBLE_PRESS", "B"): double_press_b,
    ("SHORT_PRESS", "A"): short_press_a,
    ("SHORT_PRESS", "B"): short_press_b,
    ("LONG_PRESS", "A"): long_press_a,
    ("LONG_PRESS", "B"): long_press_b,
}

holding_actions = {
    ("DOUBLE_PRESS", "A"): double_press_a_holding_b,
    ("DOUBLE_PRESS", "B"): double_press_b_holding_a,
    ("SHORT_PRESS", "A"): short_press_a_holding_b,
    ("SHORT_PRESS", "B"): short_press_b_holding_a,
    ("LONG_PRESS", "A"): long_press_a_holding_b,
    ("LONG_PRESS", "B"): long_press_b_holding_a,
}


def handle_input(input_, button):
    if button == "A" and button_b.is_holding:
        holding_actions.get((input_, button), lambda: None)()
    elif button == "B" and button_a.is_holding:
        holding_actions.get((input_, button), lambda: None)()
    else:
        actions.get((input_, button), lambda: None)()


while True:
    inputs_a = button_a.update()
    for input_ in inputs_a:
        handle_input(input_, "A")
    inputs_b = button_b.update()
    for input_ in inputs_b:
        handle_input(input_, "B")
    time.sleep(0.0025)
