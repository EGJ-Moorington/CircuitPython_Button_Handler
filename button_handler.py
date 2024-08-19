# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: MIT
"""
`button_handler`
================================================================================

This helper library simplifies the usage of buttons with CircuitPython,
by detecting and differentiating button inputs,
returning a set of the inputs and calling their corresponding functions.


* Author(s): EGJ Moorington

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

# imports
from keypad import Event, EventQueue

try:
    from supervisor import ticks_ms  # type: ignore
except ImportError:
    from time import time

    start_time = time()

    def ticks_ms() -> int:
        return int((time() - start_time + 536805.912) * 1000) & _TICKS_MAX


try:
    from typing import Callable, Literal, TypeAlias, Union  # noqa: F401
except ImportError:
    pass

__version__ = "2.0.0"
__repo__ = "https://github.com/EGJ-Moorington/CircuitPython_Button_Handler.git"

_TICKS_PERIOD = 1 << 29
_TICKS_MAX = _TICKS_PERIOD - 1


def timestamp_diff(time1: int, time2: int) -> int:
    """
    Compute the difference between two ticks values,
    assuming that they are within 2\\ :sup:`28` ticks.

    :param int time1: The minuend of the time difference, in milliseconds.
    :param int time2: The subtrahend of the time difference, in milliseconds.
    :return int: The difference between the two ticks values, in milliseconds.
    """
    diff = (time1 - time2) & _TICKS_MAX
    return diff


class ButtonInitConfig:
    """Holds configuration values to pass when a :class:`ButtonHandler` object is initialised."""

    def __init__(
        self,
        enable_multi_press: bool = True,
        multi_press_interval: float = 175,
        long_press_threshold: float = 1000,
        max_multi_press: int = 2,
    ) -> None:
        """
        :param bool enable_multi_press: Sets :attr:`.enable_multi_press`
            (whether to track multi presses).
        :param float multi_press_interval: Sets :attr:`.multi_press_interval`
            (the time frame within which two presses should occur to count as a multi press).
        :param float long_press_threshold: Sets :attr:`.long_press_threshold`
            (the minimum length of a press to count as a long press).
        :param int max_multi_press: Sets :attr:`.max_multi_press`
            (the maximum amount of presses a multi press can have).

        .. attribute:: enable_multi_press
            :type: bool
            :value: enable_multi_press = True

            Whether to account for the possibility of another short press
            following a short press and counting as a multi press.
            If set to false, :meth:`ButtonHandler.update`
            returns ``SHORT_PRESS`` immediately after a short press.

        .. attribute:: long_press_threshold
            :type: float
            :value: long_press_threshold = 1000

            The minimum length of a press to count as a long press,
            and the time the button should be pressed before counting as being held down.

        .. attribute:: max_multi_press
            :type: int
            :value: max_multi_press = 2

            The maximum amount of button presses that a multi press can be.
            :meth:`ButtonHandler.update` returns the appropiate ``_MULTI_PRESS`` immediaetly after
            the button has been pressed this many times.

        .. attribute:: multi_press_interval
            :type: float
            :value: multi_press_interval = 175

            The time frame from a button release within which
            another release should occur to count as a multi press.
        """
        self.enable_multi_press = enable_multi_press
        self.long_press_threshold = long_press_threshold
        self.max_multi_press = max_multi_press
        self.multi_press_interval = multi_press_interval


class Button:
    """Contains information about a single button."""

    def __init__(
        self, button_number: int = 0, config: ButtonInitConfig = ButtonInitConfig()
    ) -> None:
        """
        :param int button_number: Sets :attr:`._button_number`
            (the number associated with the button).
        :param ButtonInitConfig config: The :class:`ButtonInitConfig` object used to initialise
            the button's settings (:attr:`.enable_multi_press`, :attr:`.long_press_threshold`,
            :attr:`.max_multi_press` and :attr:`.multi_press_interval`).
        :raise ValueError: if *button_number* is smaller than 0.

        .. attribute:: enable_multi_press
            :type: bool
            :value: config.enable_multi_press = True

            Whether to account for the possibility of another short press
            following a short press and counting that as a multi press. If set to false,
            :meth:`ButtonHandler.update` returns ``SHORT_PRESS`` immediately after a short press.

        .. attribute:: long_press_threshold
            :type: float
            :value: config.long_press_threshold = 1000

            The minimum length of a press to count as a long press,
            and the time the button should be pressed before counting as being held down.

        .. attribute:: max_multi_press
            :type: int
            :value: config.max_multi_press = 2

            The maximum amount of button presses that a multi press can be.
            :meth:`ButtonHandler.update` returns the appropiate ``_MULTI_PRESS`` immediaetly after
            the button has been pressed this many times.

        .. attribute:: multi_press_interval
            :type: float
            :value: config.multi_press_interval = 175

            The time frame from a button release within which
            another release should occur to count as a multi press.

        .. caution:: Attributes with a *leading underscore (_)* are meant for **internal use only**,
            and accessing them may cause **unexpected behaviour**. Please consider accessing
            a *property* (if available) instead.

        .. attribute:: _button_number
            :type: int
            :value: button_number = 0

            The index number associated with the button.
            *Consider using* :attr:`.button_number` *instead*.

        .. attribute:: _is_holding
            :type: bool
            :value: False

            Whether the button has been held down for at least the time specified
            by :attr:`.long_press_threshold`. *Consider using* :attr:`.is_holding` *instead*.

        .. attribute:: _is_pressed
            :type: bool
            :value: False

            Whether the button is currently pressed.
            *Consider using* :attr:`.is_pressed` *instead*.

        .. attribute:: _last_press_time
            :type: float | None
            :value: None

            The time (in miliseconds, tracked by :meth:`supervisor.ticks_ms`) that has passed since
            the start of the previous press of a multi press. It is set to :type:`None`
            after the time specified by :attr:`.multi_press_interval` has passed.

        .. attribute:: _press_count
            :type: int
            :value: 0

            The amount of times the button has been pressed since the last
            multi press ended. It is set to 0 if the time set
            by :attr:`.multi_press_interval` passes after a short press.

        .. attribute:: _press_start_time
            :type: float
            :value: ticks_ms()

            The time (in milliseconds, tracked by :meth:`supervisor.ticks_ms`)
            at which the last button press began.
        """
        if button_number < 0:
            raise ValueError("button_number must be non-negative.")
        self._button_number = button_number
        self.enable_multi_press = config.enable_multi_press
        self.long_press_threshold = config.long_press_threshold
        self.max_multi_press = config.max_multi_press
        self.multi_press_interval = config.multi_press_interval

        self._last_press_time = None
        self._press_count = 0
        self._press_start_time = ticks_ms()
        self._is_holding = False
        self._is_pressed = False

    @property
    def button_number(self):
        """
        The index number associated with the button.

        :type: int
        """
        return self._button_number

    @property
    def is_holding(self):
        """
        Whether the button has been held down for at least the time
        specified by :attr:`.long_press_threshold`.

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
        """
        .. caution:: Methods with a *leading underscore (_)* are meant for **internal use only**,
            and calling them may cause **unexpected behaviour**. Please refrain from using them.

        Check whether a multi press has ended.
        If it has, return the amount of times the button was pressed in that multi press.

        :param int current_time: The current time, provided by :meth:`supervisor.ticks_ms`.
        :return: The amount of times the button was pressed in a multi press,
            if a multi press has ended.
        :rtype: int or None
        """
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
        """
        .. caution:: Methods with a *leading underscore (_)* are meant for **internal use only**,
            and calling them may cause **unexpected behaviour**. Please refrain from using them.

        Check whether the button has been held down for at least
        the time specified by :attr:`.long_press_threshold`.

        :param int current_time: The current time, provided by :meth:`supervisor.ticks_ms`.
        :return: Whether the button just began being held down.
        :rtype: bool
        """
        if (
            not self._is_holding
            and self._is_pressed
            and timestamp_diff(current_time, self._press_start_time) >= self.long_press_threshold
        ):
            self._is_holding = True
            return True
        return False


class ButtonInput:
    """Defines a button's input's characteristics."""

    def __init__(
        self,
        action: Union[Literal["SHORT_PRESS", "LONG_PRESS", "HOLD", "DOUBLE_PRESS"], str],
        button_number: int = 0,
        callback: Callable[[], None] = lambda: None,
        timestamp: int = 0,
    ) -> None:
        """
        :param InputAction action: Sets :attr:`action` (the action associated with the input).
        :param int button_number: Sets :attr:`button_number`
            (the number of the button associated with the input).
        :param Callable[[], None] callback: Sets :attr:`callback` (the callback associated
            with the input).
        :param int timestamp: Sets :attr:`timestamp` (the time at which the input was performed).

        .. type:: InputAction
            :canonical: Literal["SHORT_PRESS", "LONG_PRESS", "HOLD", "DOUBLE_PRESS"] | str

        .. attribute:: button_number
            :type: int
            :value: button_number = 0

            The index number of the button associated with the input.

        .. attribute:: callback
            :type: Callable[[], None]
            :value: callback = lambda: None

            The function to call when the input is detected
            and returned by :meth:`ButtonHandler.update`

        .. attribute:: timestamp
            :type: int
            :value: timestamp = 0

            The timestamp (in milliseconds, provided by :meth:`supervisor.ticks_ms`)
            at which the input was performed.

        .. caution:: Attributes with a *leading underscore (_)* are meant for
            **internal use only**, and accessing them may cause **unexpected behaviour**.
            Please consider accessing a *property* (if available) instead.

        .. attribute:: _action
            :type: InputAction
            :value: action

            The action associated with the input. *Consider accessing* :attr:`action` *instead*.
        """
        self.action = action
        self.button_number = button_number
        self.callback = callback
        self.timestamp = timestamp

    @property
    def action(self):
        """
        The action associated with the input.

        :type: InputAction
        :param InputAction action: The action associated with the input.
        :raise ValueError: if action is not a valid action. Valid actions are ``LONG_PRESS``,
            ``HOLD``, ``SHORT_PRESS`` (exactly the same as ``1_MULTI_PRESS``),
            ``DOUBLE_PRESS`` (exactly the same as ``2_MULTI_PRESS``) and
            ``x_MULTI_PRESS`` where x is an :type:`int` bigger than 0.

        """
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
        """
        .. note:: This method defines the functionality of *the equality operator (==).
            Consider using it instead*.

        Return whether two :class:`ButtonInput` objects are the same.
        True if both :attr:`action` and :attr:`button_number` are the same in both objects.

        :param object other: The object to compare the input to.
        :return: Whether the two objects are the same.
        :rtype: bool
        """
        if isinstance(other, ButtonInput):
            return self._action == other._action and self.button_number == other.button_number
        return False

    def __hash__(self) -> int:
        """
        .. note:: This method is called by :meth:`hash`. *Consider using it instead*.

        Hash a :class:`ButtonInput` object to an :type:`int`.

        :return: The hash value of the input.
        :rtype: int

        .. seealso:: :meth:`__eq__` - two :class:`ButtonInput` objects hash to the same value
            if they are equal.
        """
        return hash((self.action, self.button_number))

    def __str__(self) -> str:
        """
        .. note:: This method is called by :meth:`str`. *Consider using it instead*.

        Return a concise string representaton of the :class:`ButtonInput` object.

        :return: The string representation.
        :rtype: str
        """
        return f"{self.action} on button {self.button_number}"


class ButtonHandler:
    """Handles different types of button presses."""

    def __init__(
        self,
        event_queue: EventQueue,
        callable_inputs: set[ButtonInput],
        button_amount: int = 1,
        config: dict[int, ButtonInitConfig] = None,
    ) -> None:
        """
        :param keypad.EventQueue event_queue: Sets :attr:`_event_queue`
            (the :class:`keypad.EventQueue` object the handler should read events from).
        :param set[ButtonInput] callable_inputs: Sets :attr:`callable_inputs`
            (the :class:`ButtonInitConfig` objects used to define the callback functions).
        :param int button_amount: The amount of buttons scanned by the :mod:`keypad` scanner
            that created the event_queue parameter's argument :class:`keypad.EventQueue` object.
        :param dict[int, ButtonInitConfig] config: A dictionary containing
            :class:`ButtonInitConfig` objects used to initialise :class:`Button` objects.
            The dictionary's keys should be the index numbers of the target buttons.
            For each button that doesn't have a :class:`ButtonInitConfig` attached to it, an object
            containing the default values is created.
        :raise ValueError: if *button_amount* is smaller than 1, or if it is not an :type:`int`..

        .. attribute:: callable_inputs
            :type: set[ButtonInput]
            :value: callable_inputs

            A set of :class:`ButtonInput` objects used
            to define which functions to call when a specific input is detected.

        .. caution:: Attributes with a *leading underscore (_)* are meant for **internal use only**,
            and accessing them may cause **unexpected behaviour**. Please consider accessing
            a *property* (if available) instead.

        .. attribute:: _event
            :type: keypad.Event
            :value: Event()

            The :class:`keypad.Event` object used to store the next event to handle.

        .. attribute:: _event_queue
            :type: keypad.EventQueue
            :value: event_queue

            The :class:`keypad.EventQueue` object the handler should read events from.
        """
        if not isinstance(button_amount, int) or button_amount < 1:
            raise ValueError("button_amount must be bigger than 0.")

        self.callable_inputs = callable_inputs

        self._buttons: list[Button] = []
        for i in range(button_amount):  # Create a Button object for each button to handle
            if config:
                conf = config.get(i, ButtonInitConfig())
            else:
                conf = ButtonInitConfig()
            self._buttons.append(Button(i, conf))

        self._event = Event()
        self._event_queue = event_queue

    @property
    def buttons(self) -> list[Button]:
        """
        The :class:`Button` objects that the handler handles.

        :return: The list of :class:`Button` objects that the handler handles.
        :rtype: list[Button]
        """
        return self._buttons

    def update(self) -> set[ButtonInput]:
        """
        Check if any button ended a multi press since the last time this method was called,
        process the next :class:`keypad.Event` in :attr:`_event_queue`, call all the relevant
        callback functions and return a set of the detected :class:`ButtonInput`\\ s.

        :return: Returns a set containing all of the detected :class:`ButtonInput`\\ s
        :rtype: set[ButtonInput]
        """
        inputs = set()

        inputs.update(self._handle_buttons())

        event = self._event
        event_queue = self._event_queue
        while event_queue:
            event_queue.get_into(event)
            input_ = self._handle_event(event)
            if input_:
                inputs.add(input_)

        self._call_callbacks(inputs)
        return inputs

    def _call_callbacks(self, inputs: set[ButtonInput]) -> None:
        """
        .. caution:: Methods with a *leading underscore (_)* are meant for **internal use only**,
            and calling them may cause **unexpected behaviour**. Please refrain from using them.

        Call the callback function associated with every :class:`ButtonInput` object detected
        during execution of :meth:`.update`.

        :param set[ButtonInput] inputs: A set containing every input
            whose callback is to be called.
        """
        for input_ in inputs:
            if not input_ in self.callable_inputs:
                continue
            for callable_input in self.callable_inputs:
                if callable_input == input_:
                    callable_input.callback()

    def _handle_buttons(self) -> set[ButtonInput]:
        """
        .. caution:: Methods with a *leading underscore (_)* are meant for **internal use only**,
            and calling them may cause **unexpected behaviour**. Please refrain from using them.

        Check if any button began being held down since the last time this mehod was called
        and if any multi press ended, and return every detected :class:`ButtonInput`.

        :return: A set containing every detected :class:`ButtonInput`.
        :rtype: set[ButtonInput]
        """
        inputs = set()
        current_time = ticks_ms()
        for button in self._buttons:
            if button._is_held(current_time):
                inputs.add(ButtonInput("HOLD", button.button_number, timestamp=current_time))
            else:
                num = button._check_multi_press_timeout(current_time)
                if num:
                    inputs.add(
                        ButtonInput(
                            f"{num}_MULTI_PRESS", button.button_number, timestamp=current_time
                        )
                    )
        return inputs

    def _handle_event(self, event: Event) -> Union[ButtonInput, None]:
        """
        .. caution:: Methods with a *leading underscore (_)* are meant for **internal use only**,
            and calling them may cause **unexpected behaviour**. Please refrain from using them.

        Process a :class:`keypad.Event` and return a :class:`ButtonInput` based on it.

        :param keypad.Event event: The :class:`keypad.Event` object to process.
        :return: The detected :class:`ButtonInput`, if any.
        :rtype: ButtonInput or None
        """
        button = self._buttons[event.key_number]
        if event.pressed:  # Button just pressed
            button._is_pressed = True
            button._press_start_time = event.timestamp
            button._last_press_time = event.timestamp
            button._press_count += 1

        else:  # Button just released
            button._is_pressed = False
            if (
                timestamp_diff(event.timestamp, button._press_start_time)
                < button.long_press_threshold
            ):  # Short press
                if not button.enable_multi_press:
                    input_ = ButtonInput("SHORT_PRESS", event.key_number, timestamp=event.timestamp)
                elif button._press_count == button.max_multi_press:
                    input_ = ButtonInput(
                        f"{button.max_multi_press}_MULTI_PRESS",
                        event.key_number,
                        timestamp=event.timestamp,
                    )
                else:  # More short presses could follow
                    return None
            else:
                input_ = ButtonInput("LONG_PRESS", event.key_number, timestamp=event.timestamp)
                button._is_holding = False
            button._last_press_time = None
            button._press_count = 0
            return input_
