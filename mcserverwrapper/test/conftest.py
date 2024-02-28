# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# Needed for making pytest fixtures working correctly
# pylint: disable=wrong-import-position

"""
    Pytest configuration
"""
import os
import sys
import pathlib

# Adding source path to sys path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
sys.path.append(f"{pathlib.Path(__file__).parent.parent}")
sys.path.append(f"{pathlib.Path(__file__).parent}")

test_files_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
if not os.path.isdir(test_files_path):
    os.mkdir(test_files_path)

#pylint: enable=wrong-import-position
