"""Defines pytest fixtures"""

import shutil
import os

import pytest
import requests

from . import helpers

@pytest.fixture
def newest_server_jar():
    """Download the newest server jar version and return the jar file path"""

    url = "https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar"
    filename = os.path.join("testdir_persistent", "server.jar")

    os.makedirs("testdir_persistent", exist_ok=True)

    if not os.path.isfile(filename):
        req = requests.get(url, timeout=5)
        with open(filename, 'wb') as file:
            file.write(req.content)

    helpers.setup_workspace()

    testdir_filename = os.path.join("testdir", "server.jar")
    shutil.copyfile(filename, testdir_filename)

    return "server.jar"
