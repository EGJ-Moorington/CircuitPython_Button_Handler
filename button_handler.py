# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: MIT
"""
`button_handler`
================================================================================

This helper library simplifies the usage of buttons with CircuitPython, by detecting and
differentiating button inputs, and returning a list of the inputs.


* Author(s): EGJ Moorington

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

# imports
from keypad import Event, EventQueue
from supervisor import ticks_ms  # type: ignore

try:
    from typing import Literal, Union  # noqa: F401
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/EGJ-Moorington/CircuitPython_Button_Handler.git"

_TICKS_PERIOD = 1 << 29
_TICKS_MAX = _TICKS_PERIOD - 1


def timestamp_diff(time1: int, time2: int) -> int:
    """Compute the signed difference between two ticks values,
    assuming that they are within 2**28 ticks"""
    diff = (time1 - time2) & _TICKS_MAX
    return diff


class ButtonInitConfig:
    """
    A class that holds configuration values to pass when a :class:`ButtonHandler`
    object is initialised.

    :ivar float debounce_time: The time to wait after the state of the button changes before
        reading it again, to account for possible false triggers.
    :ivar float double_press_interval: The time frame from a button release within which
        another release should occur to count as a double press.
    :ivar float long_press_threshold: The minimum length of a press to count as a long press,
        and the time the button should be pressed before counting as being held down.
    :ivar bool enable_multi_press: Whether to account for the possibility of another short press
        following a short press and counting that as a double press.
        If set to false, :meth:`ButtonHandler.update`
        returns ``SHORT_PRESS`` immediately after a short press.
    """

    def __init__(
        self,
        enable_multi_press: bool = True,
        multi_press_interval: float = 175,
        long_press_threshold: float = 1000,
        max_multi_press: int = 2,
    ) -> None:
        """
        :param bool enable_multi_press: Sets :attr:`.enable_multi_press`
            (whether to track double presses).
        :param float double_press_interval: Sets :attr:`.double_press_interval`
            (the time frame within which two presses should occur to count as a double press).
        :param float long_press_threshold: Sets :attr:`.long_press_threshold`
            (the minimum length of a press to count as a long press).
        :param float debounce_time: Sets :attr:`.debounce_time`
            (the timeout applied to the debounce logic).
        """
        self.enable_multi_press = enable_multi_press
        self.long_press_threshold = long_press_threshold
        self.max_multi_press = max_multi_press
        self.multi_press_interval = multi_press_interval


class Button:
    def __init__(
        self, button_number: int = 0, config: ButtonInitConfig = ButtonInitConfig()
    ) -> None:
        if button_number < 0:
            raise ValueError("button_number must be non-negative.")
        self._button_number = button_number
        self.enable_multi_press = config.enable_multi_press
        self.long_press_threshold = config.long_press_threshold
        self.max_multi_press = config.max_multi_press
        self.multi_press_interval = config.multi_press_interval

        self._last_press_time = None
        self._press_count = 0
        self._press_start_time = 0
        self._is_holding = False
        self._is_pressed = False

    @property
    def button_number(self):
        return self._button_number

    @property
    def is_holding(self):
        """
        Whether the button has been held down for at least the time
        specified by :attr:`long_press_threshold`.

        :type: bool
        """
        return self._is_holding

    @property
    def is_pressed(self):
        """
        Whether the button is currently pressed.

        :type: bool
        """
        return self._is_pressed

    def _check_multi_press_timeout(self, current_time: int) -> Union[int, None]:
        if (
            self._press_count > 0
            and not self._is_pressed
            and timestamp_diff(current_time, self._last_press_time) > self.multi_press_interval
        ):
            press_count = self._press_count
            self._last_press_time = None
            self._press_count = 0
            return press_count
        return None

    def _is_held(self, current_time: int) -> bool:
        if (
            not self._is_holding
            and self._is_pressed
            and timestamp_diff(current_time, self._press_start_time) >= self.long_press_threshold
        ):
            self._is_holding = True
            return True
        return False


class ButtonInput:
    def __init__(
        self,
        action: Union[Literal["SHORT_PRESS", "LONG_PRESS", "HOLD", "DOUBLE_PRESS"], str],
        button_number: int = 0,
        timestamp: int = 0,
    ) -> None:
        self.action = action
        self.button_number = button_number
        self.timestamp = timestamp

    @property
    def action(self):
        return self._action

    @action.setter
    def action(
        self, action: Union[Literal["SHORT_PRESS", "LONG_PRESS", "HOLD", "DOUBLE_PRESS"], str]
    ):
        if action in {"SHORT_PRESS", "LONG_PRESS", "HOLD"}:
            self._action = action
            return
        try:
            if action == "DOUBLE_PRESS":
                action = "2_MULTI_PRESS"
            if not action.endswith("_MULTI_PRESS"):
                raise ValueError
            num = int(action.split("_")[0])
            if num < 1:
                raise ValueError
            if num == 1:
                action = "SHORT_PRESS"
            self._action = action
        except ValueError:
            raise ValueError(f"Invalid action: {action}.")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ButtonInput):
            return self._action == other._action and self.button_number == other.button_number
        return False

    def __hash__(self) -> int:
        return hash((self.action, self.button_number))

    def __str__(self) -> str:
        return f"{self.action} on button {self.button_number}"


class ButtonHandler:
    """
    Handles different types of button presses.

    .. caution:: Variables with a *leading underscore (_)* are meant for **internal use only**,
        and accessing them may cause **unexpected behaviour**. Please consider accessing
        a property (if available) instead.

    :ivar float debounce_time: The time to wait after the state of the button changes before
        reading it again, to account for possible false triggers.
    :ivar float double_press_interval: The time frame from a button release within which
        another release should occur to count as a double press.
    :ivar float long_press_threshold: The minimum length of a press to count as a long press,
        and the time the button should be pressed before counting as being held down.
    :ivar bool enable_multi_press: Whether to account for the possibility of another short press
        following a short press and counting that as a double press. If set to false, :meth:`update`
        returns ``SHORT_PRESS`` immediately after a short press.

    :ivar DigitalInOut _button: The :class:`DigitalInOut` object of the pin
        connected to the button.
    :ivar _first_press_time: The time (in seconds) that has passed since the start of the first
        press of a double press. It is set to None after the time specified by
        :attr:`double_press_interval` has passed.
    :vartype _first_press_time: float or None
    :ivar bool _is_holding: Whether the button has been held down for at least the time specified
        by :attr:`long_press_threshold`. *Consider using* :attr:`is_holding` *instead*.
    :ivar bool _is_pressed: Whether the button is currently pressed.
        *Consider using* :attr:`is_pressed` *instead*.
    :ivar int _press_count: The amount of times the button has been pressed since the last
        double press. It is set to 0 if the time set by :attr:`double_press_interval` passes
        after a short press.
    :ivar float _press_start_time: The time (in seconds) at which the last button press began.
    :ivar bool _was_pressed: Whether the button was pressed the last time :meth:`update`
        was called.
    """

    def __init__(
        self,
        event_queue: EventQueue,
        button_amount: int = 1,
        config: dict[int, ButtonInitConfig] = {},
    ) -> None:
        """
        :param Pin pin: The pin connected to the button.
        :param ButtonInitConfig config: The configuration object to use to initialise the handler.
            If no configuration object is provided, an object containing
            the default values is created.
        """
        if button_amount < 1:
            raise ValueError("button_amount must be bigger than 1.")

        self._buttons: list[Button] = []
        i = 0
        while i < button_amount:  # Create a _Button object for each button to handle
            try:
                conf = config[i]
            except KeyError:
                conf = ButtonInitConfig()
            self._buttons.append(Button(i, conf))
            i += 1

        self._event = Event()
        self._event_queue = event_queue

    @property
    def buttons(self) -> list[Button]:
        return self._buttons

    def update(self) -> set[ButtonInput]:
        """
        Read the current state of the button and return a list containing raised "events'" strings.

        :return: Returns any number of the following strings:

            * ``HOLDING`` - if the button has been held down for :attr:`long_press_threshold`.
            * ``SHORT_PRESS`` - if the button has been pressed for less time
              than :attr:`long_press_threshold`.
            * ``LONG_PRESS`` - if the button has been pressed for more time
              than :attr:`long_press_threshold`.
            * ``DOUBLE_PRESS`` - if the button has been pressed twice
              within :attr:`double_press_interval`.

        :rtype: list[str]
        """
        inputs = set()

        inputs.update(self._handle_buttons())

        event = self._event
        event_queue = self._event_queue
        i = 0
        while i < len(event_queue):
            event_queue.get_into(event)
            input_ = self._handle_event(event)
            if input_:
                inputs.add(input_)

        return inputs

    def _handle_buttons(self) -> set(ButtonInput):
        inputs = set()
        current_time = ticks_ms()
        for button in self._buttons:
            if button._is_held(current_time):
                inputs.add(ButtonInput("HOLD", button.button_number, current_time))
            else:
                num = button._check_multi_press_timeout(current_time)
                if num:
                    inputs.add(
                        ButtonInput(f"{num}_MULTI_PRESS", button.button_number, current_time)
                    )
        return inputs

    def _handle_event(self, event: Event) -> Union[ButtonInput, None]:
        button = self._buttons[event.key_number]
        if event.pressed:  # Button just pressed
            button._is_pressed = True
            button._press_start_time = event.timestamp
            if button._press_count < button.max_multi_press:
                button._last_press_time = event.timestamp
            button._press_count += 1

        else:  # Button just released
            button._is_pressed = False
            if (
                timestamp_diff(event.timestamp, button._press_start_time)
                < button.long_press_threshold
            ):  # Short press
                if not button.enable_multi_press:
                    input_ = ButtonInput("SHORT_PRESS", event.key_number, event.timestamp)
                elif button._press_count == button.max_multi_press:
                    input_ = ButtonInput(
                        f"{button.max_multi_press}_MULTI_PRESS", event.key_number, event.timestamp
                    )
                else:  # More short presses could follow
                    return None
            else:
                input_ = ButtonInput("LONG_PRESS", event.key_number, event.timestamp)
                button._is_holding = False
            button._last_press_time = None
            button._press_count = 0
            return input_
