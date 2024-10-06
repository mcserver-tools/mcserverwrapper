"""Helpers for testing Vanilla servers"""

import os
from random import randint

from mcserverwrapper import Wrapper

from .common_helper import connect_mineflayer, setup_workspace, download_file, assert_port_is_free

def run_vanilla_test_url(url, offline_mode=False):
    """Run all tests for a single vanilla minecraft server url"""

    setup_workspace()

    jarfile = download_file(url)

    run_vanilla_test(jarfile, offline_mode)

def run_vanilla_test(jarfile, offline_mode=False):
    """Run all tests for a single vanilla minecraft server jar"""

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
    wrapper.startup()
    assert wrapper.server_running()

    while not wrapper.output_queue.empty():
        wrapper.output_queue.get()

    wrapper.send_command("/say Hello World")

    line = ""
    while "Hello World" not in line:
        line = wrapper.output_queue.get(timeout=10)

    # Mineflayer doesn't yet support 1.20.5+
    # https://github.com/PrismarineJS/mineflayer/issues/3405
    # https://github.com/PrismarineJS/mineflayer/issues/3406
    # MineFlayer doesn't (yet) support 1.7.10
    # https://github.com/PrismarineJS/mineflayer/issues/432
    # the other versions fail because of missing protocol data
    if wrapper.get_version().name not in ["1.7.10",
                            "1.9.1",
                            "1.9.2",
                            "1.14.2",
                            "1.20.5",
                            "1.20.6",
                            "1.21",
                            "1.21.1"]:
        bot = connect_mineflayer(port=port, offline_mode=offline_mode)
        assert bot is not None

        line = ""
        while "I spawned" not in line:
            line = wrapper.output_queue.get(timeout=5)

    wrapper.stop()

    assert not wrapper.server_running()
    # assert that the server process really stopped
    assert wrapper.server.get_child_status(0.1) is not None
