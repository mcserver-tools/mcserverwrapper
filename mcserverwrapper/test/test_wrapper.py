"""Module containing tests for the mcserverwrapper"""

import os
from multiprocessing import Process
from time import sleep
from datetime import datetime, timedelta

import pytest

from mcserverwrapper import Wrapper
from .helpers import assert_port_is_free, download_file, connect_mineflayer, get_vanilla_urls, setup_workspace, \
                     run_vanilla_test_url, run_vanilla_test
from .testable_thread import TestableThread

def test_all_vanilla(jar_version_tuple):
    """Tests all of the vanilla minecraft versions"""

    url, name = jar_version_tuple

    try:
        thread = TestableThread(target=run_vanilla_test_url, args=[url, True, name], daemon=True)
        thread.start()

        terminate_time = datetime.now() + timedelta(minutes=5)

        while terminate_time > datetime.now() and thread.is_alive():
            sleep(1)

        if thread.is_alive():
            raise TimeoutError("Test timed out")

        thread.join()
    except TimeoutError as timeout_err:
        if "Test timed out" in timeout_err.args:
            pytest.fail(f"Testing version {name} timed out")
        raise timeout_err
    # pylint: disable-next=broad-exception-caught
    except Exception as exception:
        pytest.fail(reason=f"Testing version {name} errored: {exception}")

def _test_download_all_jars(jar_download_url):
    """Download all scraped vanilla minecraft server jars"""

    url = jar_download_url

    setup_workspace()

    jarfile = download_file(url)
    assert os.path.isfile(os.path.join("testdir", jarfile))

def _test_broken_versions():
    setup_workspace()
    vanilla_urls = [
        "https://launcher.mojang.com/v1/objects/050f93c1f3fe9e2052398f7bd6aca10c63d64a87/server.jar",
        "https://launcher.mojang.com/v1/objects/a028f00e678ee5c6aef0e29656dca091b5df11c7/server.jar",
        "https://launcher.mojang.com/v1/objects/952438ac4e01b4d115c5fc38f891710c4941df29/server.jar"
    ]
    for vanilla_url in vanilla_urls:
        run_vanilla_test_url(vanilla_url)

@pytest.mark.skipif(not os.path.isfile("password.txt"),
                    reason="Cannot test online server without actual credentials present")
def test_single_vanilla_online(newest_server_jar):
    """Test a single vanilla server version"""

    run_vanilla_test(newest_server_jar)

def test_single_vanilla_offline(newest_server_jar):
    """Test a single vanilla server version in offline mode"""

    run_vanilla_test(newest_server_jar, offline_mode=True)

def test_mineflayer(newest_server_jar):
    """Test the mineflayer bot"""

    assert_port_is_free()

    start_cmd = f"java -Xmx2G -jar {newest_server_jar} nogui"

    wrapper = Wrapper(os.path.join(os.getcwd(), "testdir", newest_server_jar), server_start_command=start_cmd, print_output=False)
    wrapper.startup()
    assert wrapper.server_running()
    while not wrapper.output_queue.empty():
        wrapper.output_queue.get()

    wrapper.send_command("/say Hello World")

    line = ""
    while "Hello World" not in line:
        line = wrapper.output_queue.get(timeout=5)

    connect_mineflayer()

    line = ""
    while "I spawned" not in line:
        line = wrapper.output_queue.get(timeout=5)

    wrapper.stop()

    # assert that the server process really stopped
    assert wrapper.server.get_child_status(0.1) is not None

def _test_invalid_start_params(newest_server_jar):
    """Test a server with an invalid startup command"""

    start_cmd = f"java -Xmx2G -jar {newest_server_jar}nogui"

    wrapper = Wrapper(server_start_command=start_cmd, print_output=False,
                      server_path=os.path.join(os.getcwd(), "testdir"))
    with pytest.raises(KeyboardInterrupt):
        wrapper.startup()
