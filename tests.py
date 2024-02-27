"""Module containing tests for the mcserverwrapper"""

import os
import re
import shutil
from multiprocessing import Process
from threading import Thread
from time import sleep
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from javascript import require, On, Once, AsyncTask, once, off
mineflayer = require('mineflayer')

from wrapper import Wrapper

def test_all_vanilla():
    """Tests all of the vanilla minecraft versions"""

    with open("password.txt", "r") as f:
        assert f.read()

    _setup_workspace()

    working = 0
    failed = 0
    urls = _get_vanilla_urls()
    failed_urls = []
    for url in [item[0] for item in urls]:
        print(f"{working}/{failed + working} versions passed, " + \
              f"{len(urls) - (failed + working)} remaining", end="\r")
        try:
            proc = Process(target=_test_vanilla_url, args=[url,], daemon=True)
            proc.start()

            allowed_time = timedelta(minutes=5)
            start_time = datetime.now()

            while (datetime.now() - start_time) < allowed_time and proc.is_alive():
                sleep(1)

            if proc.is_alive():
                proc.terminate()
                raise TimeoutError("Test timed out")

            working += 1
        except TimeoutError as timeout_err:
            if "Test timed out" in timeout_err.args:
                failed += 1
                failed_urls.append(url)
                print(f"{working}/{failed + working} versions passed, " + \
                      f"{len(urls) - (failed + working)} remaining")
                print(timeout_err)
                print(urls[[item[0] for item in urls].index(url)][1])
                print(urls[[item[0] for item in urls].index(url) - 1][1])
                return
            else:
                raise timeout_err
        except Exception as exception:
            failed += 1
            failed_urls.append(url)
            print(f"{working}/{failed + working} versions passed, " + \
                  f"{len(urls) - (failed + working)} remaining")
            print(exception)
            print(urls[[item[0] for item in urls].index(url)][1])
            print(urls[[item[0] for item in urls].index(url) - 1][1])
            return

    print(f"Failed urls:{' '*20}")
    for url in failed_urls:
        print(url)

    print(f"{working}/{failed + working} versions passed, " + \
          f"{len(urls) - (failed + working)} remaining")

def _test_vanilla_url(url):
    _reset_workspace()

    jarfile = _download_file(url)
    start_cmd = f"java -Xmx2G -jar {jarfile} nogui"

    wrapper = Wrapper(command=start_cmd, output=False, server_path=os.path.join(os.getcwd(), "testdir"))
    wrapper.startup()
    assert wrapper.server_running()
    while not wrapper.output_queue.empty():
        wrapper.output_queue.get()

    wrapper.send_command("/say Hello World")
    sleep(1)
    lines = ""
    while not wrapper.output_queue.empty():
        lines += wrapper.output_queue.get()
    assert "Hello World" in lines

    bot = _connect_mineflayer()
    if bot is not None:
        sleep(5)
        lines = ""
        while not wrapper.output_queue.empty():
            lines += wrapper.output_queue.get()
        assert "I spawned" in lines

    wrapper.stop()
    sleep(5)
    assert not wrapper.server_running()

def _get_vanilla_urls():
    """Function written by @Pfefan"""

    hostname = "https://mcversions.net/"
    page = requests.get(hostname)
    links = []
    counter = 0
    soup = BeautifulSoup(page.content, 'html.parser')
    for text in soup.find_all('a',{'class':'text-xs whitespace-nowrap py-2 px-3 bg-green-700 ' + \
                                   'hover:bg-green-900 rounded text-white no-underline ' + \
                                   'font-bold transition-colors duration-200'}):
        if _version_valid(text.get('href')):
            hostname = "https://mcversions.net/" + text.get('href')
            page = requests.get(hostname)
            soup = BeautifulSoup(page.content, 'html.parser')
            for text2 in soup.find_all('a',{'class':'text-xs whitespace-nowrap py-3 px-8 ' + \
                                         'bg-green-700 hover:bg-green-900 rounded text-white ' + \
                                         'no-underline font-bold transition-colors duration-200'}):
                links.append((text2.get('href'), text.get('href')))
                counter += 1
                print(f"Found {counter:3.0f} vanilla version urls", end="\r")

    print(f"Found {counter:3.0f} vanilla version urls")
    return links

def _connect_mineflayer(address = "127.0.0.1", port = 25565):
    with open("password.txt", "r") as f:
        password = f.read().split("\n", maxsplit=1)
    bot = mineflayer.createBot({
        'host': address,
        'port': port,
        'auth': 'microsoft',
        'username': password[0],
        'password': password[1],
        'hideErrors': False 
    })

    bot_connected = [False]
    def func(bot, bot_connected):
        once(bot, 'login')
        bot_connected[0] = True

    t = Thread(target=func, args=[bot, bot_connected,], daemon=True)
    t.start()
    start_time = datetime.now()

    while not bot_connected[0]:
        if (datetime.now() - start_time) > timedelta(seconds=10):
            return None
        sleep(1)

    bot.chat('I spawned')

    return bot

def _version_valid(version):
    if not re.match(r"^/download/1\...?.?.?$", version):
        return False

    vers_split = [int(item) for item in version.rsplit("/", maxsplit=1)[1].split(".")]

    if vers_split[1] < 7:
        return False
    if vers_split[1] == 7 and (len(vers_split) < 3 or vers_split[2] < 10):
        return False
    if ".".join([str(item) for item in vers_split]) in ["1.8"]: #, "1.19"]:
        return False
    
    return True

def _download_file(url, counter=""):
    filename_split = url.rsplit('/', maxsplit=1)[1].split(".")
    local_filename = f"{filename_split[0]}{counter}.{filename_split[1]}"
    req = requests.get(url)
    with open(os.path.join( "testdir", local_filename), 'wb') as file:
        file.write(req.content)
    return local_filename

def _setup_workspace():
    if not os.path.isdir("testdir"):
        os.mkdir("testdir")

def _reset_workspace():
    for entry in os.listdir("testdir"):
        if os.path.isfile(os.path.join("testdir", entry)):
            os.remove(os.path.join("testdir", entry))
        else:
            shutil.rmtree(os.path.join("testdir", entry))

def _download_all_jars():
    os.chdir("testdir")
    urls = _get_vanilla_urls()
    for index, url in enumerate(urls):
        _download_file(url, str(index))
        print(f"Downloaded {index+1:3.0f}/{len(urls)} vanilla versions", end="\r")
    print(f"Downloaded {len(urls):3.0f}/{len(urls)} vanilla versions")
    os.chdir("..")

def _test_broken_versions():
    _setup_workspace()
    os.chdir("testdir")
    vanilla_urls = [
        "https://launcher.mojang.com/v1/objects/050f93c1f3fe9e2052398f7bd6aca10c63d64a87/server.jar",
        "https://launcher.mojang.com/v1/objects/a028f00e678ee5c6aef0e29656dca091b5df11c7/server.jar"
    ]
    for vanilla_url in vanilla_urls:
        _test_vanilla_url(vanilla_url)
    _reset_workspace()
    os.chdir("..")

def _test_mineflayer():
    links = [
        "https://launcher.mojang.com/v1/objects/952438ac4e01b4d115c5fc38f891710c4941df29/server.jar"
    ]
    _setup_workspace()

    for url in links:
        _reset_workspace()

        jarfile = _download_file(url)
        start_cmd = f"java -Xmx2G -jar {jarfile} nogui"

        wrapper = Wrapper(command=start_cmd, output=False, server_path=os.path.join(os.getcwd(), "testdir"))
        wrapper.startup()
        assert wrapper.server_running()
        while not wrapper.output_queue.empty():
            wrapper.output_queue.get()

        wrapper.send_command("/say Hello World")
        sleep(1)
        lines = ""
        while not wrapper.output_queue.empty():
            lines += wrapper.output_queue.get()
        assert "Hello World" in lines

        _connect_mineflayer()
        sleep(5)
        lines = ""
        while not wrapper.output_queue.empty():
            lines += wrapper.output_queue.get()
        assert "I spawned" in lines

        wrapper.stop()
        sleep(5)
        assert not wrapper.server_running()

if __name__ == "__main__":
    _test_mineflayer()
