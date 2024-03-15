"""Helpers for testing Forge servers"""

import os
from random import randint
import re
import subprocess

import pytest

from mcserverwrapper import Wrapper
from mcserverwrapper.src.error import ServerExitedError

from .common_helper import assert_port_is_free, download_file, setup_workspace

def install_forge(url: str):
    """Install a forge server from a given installer download url"""

    installer_jar = download_file(url)
    testdir = os.path.join(os.getcwd(), "testdir")

    with subprocess.Popen(["java", "-jar", installer_jar, "--installServer"],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT,
                          cwd=testdir) as p:
        p.wait()

    os.remove(os.path.join(testdir, installer_jar))
    os.remove(os.path.join(testdir, installer_jar + ".log"))

    for file in os.listdir(testdir):
        if re.search(r"^forge-1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?", file) is not None:
            return file

    return Exception("Forge jar file not found")

def run_forge_test_url(url, offline_mode=False):
    """Run all tests for a single forge minecraft server url"""

    setup_workspace()

    server_jar = install_forge(url)

    run_forge_test(server_jar, offline_mode)

def run_forge_test(jarfile, offline_mode=False):
    """Run all tests for a single forge minecraft server jar"""

    port = 25565
    while not assert_port_is_free(port, False):
        port = randint(25500, 25600)

    if not offline_mode:
        assert os.path.isfile("password.txt")
        assert os.access("password.txt", os.R_OK)
        with open("password.txt", "r", encoding="utf8") as f:
            assert f.read().replace(" ", "").replace("\n", "") != "", "password.txt is empty"

    start_cmd = f"java -Xmx2G -jar {jarfile} nogui"

    server_property_args = {
        "port": port,
        "levt": "flat",
        "untp": "false"
    }
    if offline_mode:
        server_property_args["onli"] = "false"

    wrapper = Wrapper(os.path.join(os.getcwd(), "testdir", jarfile), server_start_command=start_cmd, print_output=False,
                      server_property_args=server_property_args)

    try:
        wrapper.startup()
    except ServerExitedError:
        # server exited because of invalid java verison
        pytest.skip("Server exited likely due to wrong java version")

    assert wrapper.server_running()

    while not wrapper.output_queue.empty():
        wrapper.output_queue.get()

    wrapper.send_command("/say Hello World")

    line = ""
    while "Hello World" not in line:
        line = wrapper.output_queue.get(timeout=10)

    wrapper.stop()

    assert not wrapper.server_running()
    # assert that the server process really stopped
    assert wrapper.server.get_child_status(0.1) is not None
