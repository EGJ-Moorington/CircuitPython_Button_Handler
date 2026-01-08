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

See the ``examples`` directory for more complex examples, including
triple presses, configuring button press delays, and supporting
multiple buttons.

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

    from button_handler import ButtonHandler, ButtonInitConfig, ButtonInput


    def double_press():
        print("Double press detected!")


    def short_press():
        print("Short press detected!")


    def long_press():
        print("Long press detected!")


    def hold():
        print("The button began being held down!")


    actions = {
        ButtonInput(ButtonInput.DOUBLE_PRESS, callback=double_press),
        ButtonInput(ButtonInput.SHORT_PRESS, callback=short_press),
        ButtonInput(ButtonInput.LONG_PRESS, callback=long_press),
        ButtonInput(ButtonInput.HOLD, callback=hold),
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

The easiest way to contribute to the repository is by `creating an issue <https://github.com/EGJ-Moorington/CircuitPython_Button_Handler/issues/new>`_.
Add a concise title and then explain the issue or suggestion in more detail in the description. This is helpful even if you do not intend to develop a fix.
If you wish to do so, however, the repository must first be forked.

Forking the repository
----------------------

In order to add commits to this repository, it must be `forked <https://github.com/EGJ-Moorington/CircuitPython_Button_Handler/fork>`_ first.
This creates a copy of the repository you can edit. Make sure to deselect "Copy the ``main`` branch only".

The following steps explain the recommended approach to working on a fork. Git needs to be installed for this.

1. **Clone the repository.**

   Open a terminal in the directory where you wish to clone the fork, and then run the following:

   .. code-block:: shell

      git clone https://github.com/<your-github-username>/CircuitPython_Button_Handler.git

   Keep in mind the URL will be different if you changed the fork's name.

2. **Set pre-commit up.**

   This repository is set up with tools that assist in development by automatically formatting code, enforcing code standards
   and fixing issues where possible.

   For these tools to run automatically before committing, `pre-commit <https://pre-commit.com/>`_
   has to be installed. This can be done in a virtual environment in order to maintain a cleaner development setup.
   Using a virtual environment isolates dependencies, ensuring they don't conflict with other projects.

   To install ``pre-commit`` in a Python virtual environment:

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
         pre-commit install

      After installing ``pre-commit``, the necessary hooks are installed on the next ``git commit``
      or the next time ``pre-commit run`` is executed.

3. **Create a new branch.**

   To make a new branch from the ``dev`` branch:

   .. code-block:: shell

      git checkout dev
      git branch -b <branch-name>

   **For consistency, please name the branch the same as the issue it addresses with the number of the issue preceding the name.
   Write the name in** ``kebab-case`` **and with no special characters (underscores are allowed).**

   For example, the branch for `issue #26 <https://github.com/EGJ-Moorington/CircuitPython_Button_Handler/issues/26>`_
   "Update ``.readthedocs.yaml`` with Sphinx key" was "26-update-readthedocsyaml-with-sphinx-key".

4. **Commit your changes.**

   After adding your changes, commit them to the new branch by executing:

   .. code-block:: shell

      git add .
      git commit

   When ready, push the changes to GitHub with the following commands:

   .. code-block:: shell

      git remote add origin https://github.com/<your-github-username>/CircuitPython_Button_Handler.git
      git push --set-upstream origin <branch-name>

5. **Open a pull request.**

   Upon opening (or refreshing) the fork's GitHub page, a message should be visible close to the top of the page:

      This branch is 1 commit ahead of ``EGJ-Moorington/CircuitPython_Button_Handler:main``.

   Firstly, ensure the branch is up to date by pressing "Sync fork". Then, select "Contribute" > "Open pull request".

   The page will show "Open a pull request". Make sure to select ``base: dev`` and ``compare: <your-branch-name>`` in the dropdowns.

   Write a brief title and then explain the changes in the description. Finish by using a `closing keyword <https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-     to-an-issue>`_ for your issue.
