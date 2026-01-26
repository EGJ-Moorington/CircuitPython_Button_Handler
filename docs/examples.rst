Simple test
------------

Ensure your button works with this simple test.

+---------------+
| Button wiring |
+===============+
| GND           |
+---------------+
| D9            |
+---------------+

.. literalinclude:: ../examples/button_handler_simpletest.py
    :caption: examples/button_handler_simpletest.py
    :linenos:

Single button
-------------

This simple script showcases the usage of this library using a single button.

+---------------+
| Button wiring |
+===============+
| GND           |
+---------------+
| D9            |
+---------------+

.. literalinclude:: ../examples/button_handler_single_button.py
    :caption: examples/button_handler_single_button.py
    :linenos:

Advanced single button
----------------------

This advanced script demonstrates how to handle triple presses and configure a button.

+---------------+
| Button wiring |
+===============+
| GND           |
+---------------+
| D9            |
+---------------+

.. literalinclude:: ../examples/button_handler_advanced_single_button.py
    :caption: examples/button_handler_advanced_single_button.py
    :linenos:

Double button
-------------

This script showcases the usage of this library using two buttons.

+-----------------+-----------------+
| Button A wiring | Button B wiring |
+=================+=================+
| GND             | GND             |
+-----------------+-----------------+
| D9              | A2              |
+-----------------+-----------------+

.. literalinclude:: ../examples/button_handler_double_button.py
    :caption: examples/button_handler_double_button.py
    :linenos:

Advanced double button
----------------------

This advanced script demonstrates how to handle triple presses, configure buttons and handle button presses while another button is being held down.

+-----------------+-----------------+
| Button A wiring | Button B wiring |
+=================+=================+
| GND             | GND             |
+-----------------+-----------------+
| D9              | A2              |
+-----------------+-----------------+

.. literalinclude:: ../examples/button_handler_advanced_double_button.py
    :caption: examples/button_handler_advanced_double_button.py
    :linenos:
