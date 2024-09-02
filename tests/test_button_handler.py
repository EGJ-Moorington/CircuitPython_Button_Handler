# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 EGJ Moorington
#
# SPDX-License-Identifier: MIT
import sys

import pytest

sys.path.append(".")
from button_handler import *


class MockEvent(Event):
    def __init__(
        self, key_number: int = 0, pressed: bool = True, timestamp: int = ticks_ms()
    ) -> None:
        super().__init__(key_number, pressed)
        self.timestamp = timestamp


class MockEventQueue(EventQueue):
    def __init__(self, max_events):
        super().__init__(max_events)

    def get_into(self, event: MockEvent) -> bool:
        if not self._events:
            return False
        next_event = self._events.popleft()
        event._key_number = next_event._key_number
        event._pressed = next_event._pressed
        event.timestamp = next_event.timestamp
        return True

    def keypad_eventqueue_record(self, key_number, current, time):
        if len(self._events) == self._events.maxlen:
            self._overflowed = True
        else:
            self._events.append(MockEvent(key_number, current, time))


class deque:
    def __init__(self, queue: list, maxlen: int):
        self.queue = queue
        self.maxlen = maxlen

    def popleft(self):
        return self.queue.pop(0)

    def __len__(self):
        return len(self.queue)

    def append(self, item):
        self.queue.append(item)


call_amount = 0


def callback():
    global call_amount  # noqa: PLW0603
    call_amount += 1


@pytest.fixture
def event_queue() -> MockEventQueue:
    return MockEventQueue(max_events=64)


@pytest.fixture
def config() -> ButtonInitConfig:
    return ButtonInitConfig(False, 200, max_multi_press=4)


@pytest.fixture
def time() -> int:
    return ticks_ms()


@pytest.fixture
def button(config) -> Button:
    return Button(config=config)


@pytest.fixture
def input_() -> ButtonInput:
    return ButtonInput(ButtonInput.SHORT_PRESS, 3, callback, timestamp=time)


@pytest.fixture
def inputs(input_) -> set[ButtonInput]:
    return {input_, ButtonInput(ButtonInput.LONG_PRESS, callback=callback)}


@pytest.fixture
def button_handler(event_queue, config, inputs) -> ButtonHandler:
    return ButtonHandler(event_queue, inputs, 4, {1: config})


def test_timestamp_diff(time):
    time2 = time + 10000
    assert timestamp_diff(time2, time) == 10000
    time2 = time + 90000
    assert timestamp_diff(time2, time) == 90000


class TestButtonInitConfig:
    def test_init(self, config):
        assert config.enable_multi_press == False
        assert config.multi_press_interval == 200
        assert config.long_press_threshold == 1000
        assert config.max_multi_press == 4


class TestButton:
    def test_init(self, button):
        assert button.button_number == 0
        assert button.enable_multi_press == False
        assert button.long_press_threshold == 1000
        assert button.max_multi_press == 4
        assert button.multi_press_interval == 200

        assert button.button_number == button._button_number
        assert button.is_holding == button._is_holding
        assert button.is_pressed == button._is_pressed

        with pytest.raises(ValueError):
            button = Button(-1)

    def test__check_multi_press_timeout(self, time, button: Button):
        assert button._check_multi_press_timeout(time) == None
        button._press_count += 2
        button._last_press_time = time - button.multi_press_interval * 2
        assert button._check_multi_press_timeout(time) == 2

    def test__is_held(self, time, button: Button):
        button._is_pressed = True
        assert button._is_held(time + 250) == False
        button._press_start_time = time - button.long_press_threshold * 2
        assert button._is_held(time) == True


class TestButtonInput:
    def test_init(self, input_):
        assert input_.action == ButtonInput.SHORT_PRESS
        assert input_.button_number == 3
        assert input_.callback() == None
        assert input_.timestamp == time

        with pytest.raises(ValueError):
            input_.action = 0

    def test_valid_action(self, input_):
        assert input_._action == input_.action
        input_.action = ButtonInput.LONG_PRESS
        assert input_.action == ButtonInput.LONG_PRESS
        input_.action = 3
        assert input_.action == 3

    @pytest.mark.parametrize(
        "action",
        {
            0,
            "",
            "w",
            None,
            -1,
            3.0,
        },
    )
    def test_invalid_action(self, input_, action):
        with pytest.raises(ValueError):
            input_.action = action

    def test_dunder(self, input_: ButtonInput, time):
        assert input_ == ButtonInput(ButtonInput.SHORT_PRESS, 3, timestamp=time * 2)

        assert hash(input_) == hash((input_.action, input_.button_number))

        assert str(input_) == f"{ButtonInput.SHORT_PRESS} on button 3"


class TestButtonHandler:
    def sim_press(self, button: Button, handler: ButtonHandler, press, press_count=1):
        queue = handler._event_queue
        match press:
            case "SHORT_PRESS":
                length = button.long_press_threshold - 825
            case "LONG_PRESS":
                length = button.long_press_threshold + 100
        start_time = ticks_ms() - length

        queue.keypad_eventqueue_record(button.button_number, True, start_time)
        start = handler.update()
        button._press_count = press_count
        queue.keypad_eventqueue_record(button.button_number, False, ticks_ms())
        return start

    def test_init(self, button_handler: ButtonHandler, input_, config: ButtonInitConfig):
        assert input_ in button_handler.callable_inputs
        assert len(button_handler.buttons) == 4
        assert button_handler.buttons[1].max_multi_press == config.max_multi_press

    @pytest.mark.parametrize("amount", {0, 1.2, -1})
    def test_invalid_button_amount(self, amount, event_queue):
        with pytest.raises(ValueError):
            ButtonHandler(event_queue, set(), button_amount=amount)

    def test__call_callbacks(self, inputs, button_handler: ButtonHandler):
        global call_amount  # noqa: PLW0603
        call_amount = 0
        inputs.add(ButtonInput(ButtonInput.HOLD))
        button_handler._call_callbacks(inputs)
        assert call_amount == 2

    def test__handle_buttons(self, button_handler: ButtonHandler, time):
        inputs = button_handler._handle_buttons()
        assert inputs == set()

        button = button_handler.buttons[2]
        button._is_pressed = True
        button._press_start_time = time - button.long_press_threshold * 2
        inputs = button_handler._handle_buttons()
        assert inputs == {ButtonInput(ButtonInput.HOLD, 2)}

        button = button_handler.buttons[3]
        button._press_count = 3
        button._last_press_time = time - button.multi_press_interval * 2
        inputs = button_handler._handle_buttons()
        assert inputs == {ButtonInput(3, 3)}

    def test__handle_event(self, time, button_handler: ButtonHandler):
        button = button_handler.buttons[1]
        button._button_number = 1

        event = MockEvent(1, True, time)
        button._last_press_time = 0
        button_handler._handle_event(event)
        assert button.is_pressed
        assert button._press_start_time == event.timestamp
        assert button._last_press_time == event.timestamp
        assert button._press_count == 1

        button._press_start_time = time - button.long_press_threshold // 2
        button.enable_multi_press = False
        event = MockEvent(1, False, time)
        assert button_handler._handle_event(event) == ButtonInput(ButtonInput.SHORT_PRESS, 1)

        button.enable_multi_press = True
        assert button_handler._handle_event(event) == None

        button._press_count = 4
        assert button_handler._handle_event(event) == ButtonInput(4, 1)

        button._press_start_time = time - button.long_press_threshold * 2
        assert button_handler._handle_event(event) == ButtonInput(ButtonInput.LONG_PRESS, 1)

        assert button._last_press_time == None
        assert button._press_count == 0

    def test_update(self, button_handler: ButtonHandler, time):
        queue: MockEventQueue = button_handler._event_queue
        button = button_handler.buttons[2]

        # Incomplete multi press + timeout
        assert self.sim_press(button, button_handler, "SHORT_PRESS") == set()
        input_set = button_handler.update()
        assert input_set == set()
        while input_set == set() and timestamp_diff(ticks_ms(), time) < 100:
            input_set = button_handler.update()
        assert input_set.pop() == ButtonInput(ButtonInput.SHORT_PRESS, 2)

        # Multi press disabled
        button = button_handler.buttons[1]
        assert self.sim_press(button, button_handler, "SHORT_PRESS", 4) == set()
        assert button_handler.update().pop() == ButtonInput(ButtonInput.SHORT_PRESS, 1)

        # Finish max multi press
        self.sim_press(button, button_handler, "SHORT_PRESS")
        button._press_count = 4
        button.enable_multi_press = True
        assert button_handler.update().pop() == ButtonInput(4, 1)

        # Long press
        button._press_start_time = time - button.long_press_threshold * 2
        queue.keypad_eventqueue_record(1, False, time)
        assert button_handler.update().pop() == ButtonInput(ButtonInput.LONG_PRESS, 1)
