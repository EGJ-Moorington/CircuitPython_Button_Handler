Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-button-handler/badge/?version=latest
    :target: https://circuitpython-button-handler.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/EGJ-Moorington/CircuitPython_Button_Handler/workflows/Build%20CI/badge.svg
    :target: https://github.com/EGJ-Moorington/CircuitPython_Button_Handler/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

This helper library simplifies the usage of buttons with CircuitPython, by detecting and differentiating button inputs, returning a set of the inputs and calling their corresponding functions.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-button-handler/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-button-handler

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-button-handler

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-button-handler

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install button_handler

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

This simple script showcases the usage of this library using a single button.

+---------------+
| Button wiring |
+===============+
| GND           |
+---------------+
| D9            |
+---------------+

.. code-block:: python

    import time

    import board
    from keypad import Keys

    from button_handler import ButtonHandler


    def double_press():
        print("Double press detected!")


    def short_press():
        print("Short press detected!")


    def long_press():
        print("Long press detected!")


    def hold():
        print("The button began being held down!")


    actions = {
        "DOUBLE_PRESS": double_press,
        "SHORT_PRESS": short_press,
        "LONG_PRESS": long_press,
        "HOLD": hold,
    }

    scanner = Keys([board.D9], value_when_pressed=False)
    button_handler = ButtonHandler(scanner.events, actions)


    while True:
        button_handler.update()
        time.sleep(0.0025)

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-button-handler.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/EGJ-Moorington/CircuitPython_Button_Handler/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

This repository is set up with tools that assist in development by automatically formatting code, enforcing standards,
and fixing issues where possible.

For these tools to run automatically before committing, `pre-commit <https://pre-commit.com/>`_
has to be installed. This can be done in a virtual environment in order to maintain a cleaner development setup.
Using a virtual environment isolates dependencies, ensuring they don't conflict with other projects.

The following steps explain how to install ``pre-commit`` in a Python virtual environment.

1. **Ensure Python is installed in your system.**

   You can check your version of `Python  <https://www.python.org/downloads/>`_
   with the following command:

   .. code-block:: shell

       python --version

2. **Create a Python virtual environment.**

   To make a virtual environment of name ``.venv`` in the current directory, run:

   .. code-block:: shell

       python -m venv .venv

3. **Activate the virtual environment.**

   * On Windows, run:

     .. code-block:: shell

         .\.venv\Scripts\activate

   * On Linux or macOS, run:

     .. code-block:: shell

         source .venv/bin/activate

   To avoid repeating this step every time a terminal is opened in this directory,
   configure your IDE to use the ``.venv`` virtual environment as the default interpreter.
   In Visual Studio Code, this can be done by opening the command palette, typing
   ``Python: Select Interpreter`` and selecting the ``.venv`` virtual environment.

4. **Install pre-commit.**

   This can easily be achieved by executing:

   .. code-block:: shell

       pip install pre-commit

   After installing ``pre-commit``, the necessary hooks are installed on the next ``git commit``
   or the next time ``pre-commit run`` is executed.


