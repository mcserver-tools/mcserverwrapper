"""Common helper functions used during testing"""

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
from requests.adapters import HTTPAdapter, Retry

from javascript import require, once

from mcserverwrapper.src.util import logger

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

def assert_port_is_free(port: int = 25565, strict=True) -> bool:
    """Skips the current test if the given port is not free"""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        # windows error
        except PermissionError:
            if strict:
                pytest.skip(reason=f"Port {port} is in use")
            else:
                return False
        # linux error?
        except socket.error as e:
            if e.errno in [errno.EADDRINUSE, errno.ECONNREFUSED]:
                if strict:
                    pytest.skip(reason=f"Port {port} is in use")
                else:
                    return False
            else:
                # something else raised the socket.error exception
                raise e
        return True

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
        if (datetime.now() - start_time) > timedelta(seconds=30):
            pytest.skip(f"Bot connection to {address}:{port} timed out")
        sleep(0.1)

    bot.chat('I spawned')

    return bot

def download_file(url, counter=""):
    """
    Download the file from the given url and return its path
    
    Retry code from https://stackoverflow.com/a/35504626/15436169
    """

    filename_split = url.rsplit('/', maxsplit=1)[1].rsplit(".", maxsplit=1)
    local_filename = f"{filename_split[0]}{counter}.{filename_split[1]}"
    with requests.Session() as s:
        retries = Retry(total=10,
                        backoff_factor=0.1)
        s.mount("https://", HTTPAdapter(max_retries=retries))
        req = s.get(url, timeout=30)
        with open(os.path.join("testdir", local_filename), 'wb') as file:
            file.write(req.content)
    return local_filename

def get_mcserver_log() -> str:
    """Return the current mcserverwrapper.log as a string if it exists"""

    if logger.logfile_path is None:
        print("Logger was not yet setup, cannot print logfile")
        return ""

    data = f"Printing out {logger.LOGFILE_NAME}:\n"
    with open(logger.logfile_path, "r", encoding="utf8") as f:
        for line in f.readlines():
            data += line
    return data

def get_vanilla_urls():
    """Function written by @Pfefan"""

    hostname = "https://mcversions.net/"
    session = requests.Session()
    main_page = session.get(hostname, timeout=5)
    links = []
    soup = BeautifulSoup(main_page.content, 'html.parser')
    base_links = soup.find_all('a',{'class':'text-xs whitespace-nowrap py-2 px-3 bg-green-700 ' + \
                                   'hover:bg-green-900 rounded text-white no-underline ' + \
                                   'font-bold transition-colors duration-200'})
    raw_version_urls = [link.get('href') for link in base_links]
    for version_raw in raw_version_urls:
        if re.match(r"^/download/1\...?.?.?$", version_raw):
            version_name = version_raw.rsplit("/", maxsplit=1)[1]
            if _version_valid(version_name):
                hostname = "https://mcversions.net/" + version_raw
                page = session.get(hostname, timeout=5)
                soup = BeautifulSoup(page.content, 'html.parser')
                for server_jar_link in soup.find_all('a',{'class':'text-xs whitespace-nowrap py-3 px-8 ' + \
                                            'bg-green-700 hover:bg-green-900 rounded text-white ' + \
                                            'no-underline font-bold transition-colors duration-200 downloadJar'}):
                    links.append((server_jar_link.get('href'), version_name))
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
