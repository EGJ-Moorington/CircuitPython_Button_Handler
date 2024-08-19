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
import time

from digitalio import DigitalInOut, Direction, Pull

try:
    import typing  # noqa: F401

    from board import Pin
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/EGJ-Moorington/CircuitPython_Button_Handler.git"


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
    :ivar bool enable_double_press: Whether to account for the possibility of another short press
        following a short press and counting that as a double press.
        If set to false, :meth:`ButtonHandler.update`
        returns ``SHORT_PRESS`` immediately after a short press.
    """

    def __init__(
        self,
        enable_double_press: bool = True,
        double_press_interval: float = 0.175,
        long_press_threshold: float = 1.0,
        debounce_time: float = 0.025,
    ) -> None:
        """
        :param bool enable_double_press: Sets :attr:`.enable_double_press`
            (whether to track double presses).
        :param float double_press_interval: Sets :attr:`.double_press_interval`
            (the time frame within which two presses should occur to count as a double press).
        :param float long_press_threshold: Sets :attr:`.long_press_threshold`
            (the minimum length of a press to count as a long press).
        :param float debounce_time: Sets :attr:`.debounce_time`
            (the timeout applied to the debounce logic).
        """
        self.debounce_time = debounce_time
        self.double_press_interval = double_press_interval
        self.enable_double_press = enable_double_press
        self.long_press_threshold = long_press_threshold


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
    :ivar bool enable_double_press: Whether to account for the possibility of another short press
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

    def __init__(self, pin: Pin, config: ButtonInitConfig = ButtonInitConfig()) -> None:
        """
        :param Pin pin: The pin connected to the button.
        :param ButtonInitConfig config: The configuration object to use to initialise the handler.
            If no configuration object is provided, an object containing
            the default values is created.
        """
        self._button = DigitalInOut(pin)
        self._button.direction = Direction.INPUT
        self._button.pull = Pull.UP
        self.debounce_time = config.debounce_time
        self.double_press_interval = config.double_press_interval
        self.enable_double_press = config.enable_double_press
        self.long_press_threshold = config.long_press_threshold

        self._press_count = 0
        self._press_start_time = 0
        self._first_press_time = None
        self._is_holding = False
        self._is_pressed = False
        self._was_pressed = False

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

    def update(self) -> list[str]:
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
        current_time = time.monotonic()
        self._is_pressed = not self._button.value

        # Debounce logic
        if self._is_pressed != self._was_pressed:
            time.sleep(self.debounce_time)
            self._is_pressed = not self._button.value

        events = []

        if self._is_pressed and not self._was_pressed:  # Button just pressed
            self._press_start_time = current_time
            if self._first_press_time is None:
                self._first_press_time = current_time
            self._press_count += 1

        if (
            self._is_pressed and current_time - self._press_start_time >= self.long_press_threshold
        ):  # Holding
            self._is_holding = True
            events.append("HOLDING")

        if not self._is_pressed and self._was_pressed:  # Button just released
            if current_time - self._press_start_time < self.long_press_threshold:
                if not self.enable_double_press:
                    events.append("SHORT_PRESS")
                elif self._press_count == 2:
                    events.append("DOUBLE_PRESS")
                else:
                    self._was_pressed = self._is_pressed
                    return events
            else:
                events.append("LONG_PRESS")
            self._is_holding = False
            self._first_press_time = None
            self._press_count = 0

        if (
            self._press_count == 1
            and current_time - self._first_press_time > self.double_press_interval
            and not self._is_pressed
        ):
            events.append("SHORT_PRESS")
            self._first_press_time = None
            self._press_count = 0

        self._was_pressed = self._is_pressed
        return events
