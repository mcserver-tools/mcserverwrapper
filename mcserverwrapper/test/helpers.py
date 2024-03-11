"""Helper functions used during testing"""

from datetime import datetime, timedelta
import errno
import socket
import os
import shutil
from threading import Thread
from time import sleep

import re
import pytest
from bs4 import BeautifulSoup
import requests

from javascript import require, once

from mcserverwrapper import Wrapper

mineflayer = require('mineflayer')

def setup_workspace():
    """Setup the testing folder"""

    try:
        if os.path.isdir("testdir"):
            shutil.rmtree("testdir")
        os.makedirs("testdir", exist_ok=True)
    except PermissionError as e:
        pytest.skip("cannot access testdir")

        if "[WinError 32]" in e.args:
            pytest.skip("cannot access testdir")

def reset_workspace():
    """Delete everything inside the testing folder"""

    for entry in os.listdir("testdir"):
        if os.path.isfile(os.path.join("testdir", entry)):
            os.remove(os.path.join("testdir", entry))
        else:
            shutil.rmtree(os.path.join("testdir", entry))

def assert_port_is_free(port: int = 25565) -> bool:
    """Skips the current test if the given port is not free"""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        # windows error
        except PermissionError:
            pytest.skip(reason=f"Port {port} is in use")
        # linux error?
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                pytest.skip(reason=f"Port {port} is in use")
            else:
                # something else raised the socket.error exception
                raise e

def run_vanilla_test_url(url, offline_mode=False, version_name=None):
    """Run all tests for a single vanilla minecraft server url"""

    assert_port_is_free()

    setup_workspace()

    jarfile = download_file(url)

    run_vanilla_test(jarfile, offline_mode, version_name)

def run_vanilla_test(jarfile, offline_mode=False, version_name=None):
    """Run all tests for a single vanilla minecraft server jar"""

    assert_port_is_free()

    if not offline_mode:
        assert os.path.isfile("password.txt")
        assert os.access("password.txt", os.R_OK)

    start_cmd = f"java -Xmx2G -jar {jarfile} nogui"

    server_property_args = None
    if offline_mode:
        server_property_args = {
            "onli": "false"
        }

    wrapper = Wrapper(server_start_command=start_cmd, print_output=False,
                      server_path=os.path.join(os.getcwd(), "testdir"),
                      server_property_args=server_property_args)
    wrapper.startup()
    assert wrapper.server_running()

    while not wrapper.output_queue.empty():
        wrapper.output_queue.get()

    wrapper.send_command("/say Hello World")

    line = ""
    while "Hello World" not in line:
        line = wrapper.output_queue.get(timeout=5)

    # MineFlayer doesn't (yet) support 1.7.10
    # https://github.com/PrismarineJS/mineflayer/issues/432
    # the other versions fail because of missing protocol data
    if version_name not in ["1.14.2", "1.9.2", "1.9.1", "1.7.10"]:
        bot = connect_mineflayer(offline_mode=offline_mode)
        assert bot is not None

        line = ""
        while "I spawned" not in line:
            line = wrapper.output_queue.get(timeout=5)

    wrapper.stop()

    assert not wrapper.server_running()
    # assert that the server process really stopped
    assert wrapper.server.get_child_status(0.1) is not None

def connect_mineflayer(address = "127.0.0.1", port = 25565, offline_mode=False):
    """Connect a fake player to the server"""

    if not offline_mode:
        with open("password.txt", "r", encoding="utf8") as f:
            password = f.read().split("\n")
        bot = mineflayer.createBot({
            'host': address,
            'port': port,
            'auth': 'microsoft',
            'username': password[0],
            'password': password[1],
            'hideErrors': False 
        })
    else:
        bot = mineflayer.createBot({
            'host': address,
            'port': port,
            'username': "Developer",
            'hideErrors': False 
        })

    bot_connected = [False]
    def func(bot, bot_connected):
        once(bot, 'spawn')
        bot_connected[0] = True

    t = Thread(target=func, args=[bot, bot_connected,], daemon=True)
    t.start()
    start_time = datetime.now()

    while not bot_connected[0]:
        if (datetime.now() - start_time) > timedelta(seconds=10):
            return None
        sleep(0.1)

    bot.chat('I spawned')

    return bot

def download_file(url, counter=""):
    """Download the file from the given url and return its path"""

    filename_split = url.rsplit('/', maxsplit=1)[1].split(".")
    local_filename = f"{filename_split[0]}{counter}.{filename_split[1]}"
    req = requests.get(url, timeout=5)
    with open(os.path.join("testdir", local_filename), 'wb') as file:
        file.write(req.content)
    return local_filename

def get_vanilla_urls():
    """Function written by @Pfefan"""

    hostname = "https://mcversions.net/"
    page = requests.get(hostname, timeout=5)
    links = []
    counter = 0
    soup = BeautifulSoup(page.content, 'html.parser')
    for text in soup.find_all('a',{'class':'text-xs whitespace-nowrap py-2 px-3 bg-green-700 ' + \
                                   'hover:bg-green-900 rounded text-white no-underline ' + \
                                   'font-bold transition-colors duration-200'}):
        version_raw = text.get('href')
        if re.match(r"^/download/1\...?.?.?$", version_raw):
            version_name = version_raw.rsplit("/", maxsplit=1)[1]
            if _version_valid(version_name):
                hostname = "https://mcversions.net/" + version_raw
                page = requests.get(hostname, timeout=5)
                soup = BeautifulSoup(page.content, 'html.parser')
                for text2 in soup.find_all('a',{'class':'text-xs whitespace-nowrap py-3 px-8 ' + \
                                            'bg-green-700 hover:bg-green-900 rounded text-white ' + \
                                            'no-underline font-bold transition-colors duration-200'}):
                    links.append((text2.get('href'), version_name))
                    counter += 1
                    print(f"Found {counter:3.0f} vanilla version urls", end="\r")

    print(f"Found {counter:3.0f} vanilla version urls")
    return links

def _version_valid(version):
    vers_split = [int(item) for item in version.split(".")]

    if vers_split[1] < 7:
        return False
    if vers_split[1] == 7 and (len(vers_split) < 3 or vers_split[2] < 10):
        return False
    if ".".join([str(item) for item in vers_split]) in ["1.8"]:
        return False

    return True
