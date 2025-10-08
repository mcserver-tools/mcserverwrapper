# CODE STYLE

To allow for a consistent code style within this repository, some rules are enforced.

This file documents these rules.

Note that these are not unchangeable, if given a good reason.

## imports

All imports have to be absolute. This is also enforced in the pre-commit hooks.

## sections order in code files

The order in which imports, constants, ... are defined in python source code files needs to be unified.

The different sections have to follow this order:
* module-level docstring (what does this module do / contain)
* standard library imports (e.g. `import os`)
* third-party imports (e.g. `import numpy as np`)
* local imports (e.g. `from abllib import get_logger`)
* optional modules (e.g. `try_import_module("pykakasi")`)
* pylint comments (which checks to ignore in this file)
* module-level logger
* module-level constants
* everything else

Note that not all sections need to be present.
