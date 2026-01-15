# SPDX-FileCopyrightText: Copyright (c) 2026 EGJ Moorington
#
# SPDX-License-Identifier: MIT

import re
import warnings
from pathlib import Path

START_DIRECTIVE_RE = re.compile(r"([\t ]*)(\.\. include-example:::)\s*(.*)")
END_DIRECTIVE_RE = re.compile(".. /include-example:::")
CODE_BLOCK_RE = re.compile(".. code-block::")
SETTING_RE = re.compile(r"\s*:(\S+):\s*(.*)")

README_PATH = Path("README.rst")


def indent(code: str, spaces: int | str = 4) -> str:
    prefix = spaces if isinstance(spaces, str) else " " * spaces
    return "".join(
        prefix + line if line.strip() else line for line in code.splitlines(True)
    )  # Only indent if a line, when removing all whitespace and linebreaks, is not empty


def find_used_examples(readme: str) -> set[Path]:
    used_examples = set()
    for start_directive in re.finditer(START_DIRECTIVE_RE, readme):
        used_examples.add(Path(start_directive.group(3)))

    return used_examples


def load_examples(paths: set[Path]) -> dict[str, str]:
    examples = {}

    for path in paths:
        try:
            examples[str(path)] = path.read_text().rstrip()
        except FileNotFoundError:
            warnings.warn(f"Tried to load example {path}, which does not exist.")

    return examples


def read_settings(
    settings_string: str, default_language: str = "python"
) -> tuple[dict[str, str], str]:
    settings = {}
    language = default_language
    for setting in re.finditer(SETTING_RE, settings_string):
        setting_name = setting.group(1)

        if setting_name == "language":
            language = setting.group(2)
            continue

        settings[setting_name] = setting.group(2)

    return settings, language


def update_readme(readme: str, examples_to_update: dict[str, str]) -> str:
    for start_directive in reversed(
        list(re.finditer(START_DIRECTIVE_RE, readme))
    ):  # Update readme from the bottom, so that Match indices do not change on each iteration
        example_to_insert = str(Path(start_directive.group(3)))  # Normalise the path string

        if example_to_insert not in examples_to_update.keys():
            continue

        remaining_readme = readme[start_directive.end() :]

        next_start_directive = re.search(START_DIRECTIVE_RE, remaining_readme)
        end_directive = re.search(
            END_DIRECTIVE_RE,
            remaining_readme[: next_start_directive.start() if next_start_directive else None],
        )

        if end_directive == None:
            raise SyntaxError(
                "An include-example directive was not closed:\n"
                f"{
                    readme[
                        max(start_directive.start() - 100, 0) : min(
                            start_directive.end() + 100, len(readme)
                        )
                    ]
                }"
            )

        code_block = re.search(CODE_BLOCK_RE, remaining_readme[: end_directive.start()])
        settings_string = remaining_readme[
            : code_block.start() if code_block else end_directive.start()
        ]  # Read include-example settings, ignoring code-block settings

        settings, language = read_settings(settings_string)

        settings_block = ""
        for setting, value in settings.items():
            settings_block += f":{setting}: {value}\n"

        modified_block = " ".join(start_directive.group(2, 3)) + "\n"
        modified_block += indent(f":language: {language}\n")
        modified_block += indent(settings_block)
        modified_block += "\n"
        modified_block += f".. code-block:: {language}\n"
        modified_block += indent(settings_block)
        modified_block += "\n"
        modified_block += indent(examples_to_update[example_to_insert])
        modified_block += "\n\n"
        modified_block += f"{end_directive.group()}"

        readme = (
            readme[: start_directive.start()]
            + indent(modified_block, start_directive.group(1))
            + readme[start_directive.end() + end_directive.end() :]
        )

    return readme


def main(*args):
    readme = README_PATH.read_text()
    updated_files = {Path(path_str) for path_str in args[0]}
    used_examples = find_used_examples(readme)

    required_examples = (
        used_examples if README_PATH in updated_files else used_examples & updated_files
    )

    examples = load_examples(required_examples)
    updated = update_readme(readme, examples)

    README_PATH.write_text(updated, newline="\n")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
