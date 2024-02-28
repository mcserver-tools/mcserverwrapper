"""Module containing tests for the mcserverwrapper"""

import os
from multiprocessing import Process
from time import sleep
from datetime import datetime, timedelta

from .helpers import _download_file, connect_mineflayer, get_vanilla_urls, setup_workspace, reset_workspace, run_test_vanilla_url

from mcserverwrapper.src.wrapper import Wrapper

def test_all_vanilla():
    """Tests all of the vanilla minecraft versions"""

    with open("password.txt", "r") as f:
        assert f.read()

    setup_workspace()

    working = 0
    failed = 0
    urls = get_vanilla_urls()
    failed_urls = []
    for url in [item[0] for item in urls]:
        print(f"{working}/{failed + working} versions passed, " + \
              f"{len(urls) - (failed + working)} remaining", end="\r")
        try:
            proc = Process(target=run_test_vanilla_url, args=[url,True,], daemon=True)
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

def test_download_all_jars():
    setup_workspace()
    urls = get_vanilla_urls()
    c = 0
    for url in [item[0] for item in urls]:
        _download_file(url, str(c))
        print(f"Downloaded {c+1:3.0f}/{len(urls)} vanilla versions", end="\r")
        c += 1
    print(f"Downloaded {len(urls):3.0f}/{len(urls)} vanilla versions")
    assert len(os.listdir("testdir")) == len(urls)
    reset_workspace()

def _test_broken_versions():
    setup_workspace()
    vanilla_urls = [
        "https://launcher.mojang.com/v1/objects/050f93c1f3fe9e2052398f7bd6aca10c63d64a87/server.jar",
        "https://launcher.mojang.com/v1/objects/a028f00e678ee5c6aef0e29656dca091b5df11c7/server.jar",
        "https://launcher.mojang.com/v1/objects/952438ac4e01b4d115c5fc38f891710c4941df29/server.jar"
    ]
    for vanilla_url in vanilla_urls:
        run_test_vanilla_url(vanilla_url)
    reset_workspace()

def test_single_vanilla():
    setup_workspace()
    urls = [
        "https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar"
    ]
    for vanilla_url in urls:
        run_test_vanilla_url(vanilla_url, offline_mode=True)
    reset_workspace()

def test_mineflayer():
    links = [
        "https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar"
    ]
    setup_workspace()

    for url in links:
        reset_workspace()

        jarfile = _download_file(url)
        start_cmd = f"java -Xmx2G -jar {jarfile} nogui"

        wrapper = Wrapper(server_start_command=start_cmd, print_output=False, server_path=os.path.join(os.getcwd(), "testdir"))
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

        connect_mineflayer()
        sleep(5)
        lines = ""
        while not wrapper.output_queue.empty():
            lines += wrapper.output_queue.get()
        assert "I spawned" in lines

        wrapper.stop()
        sleep(5)
        assert not wrapper.server_running()
    reset_workspace()

if __name__ == "__main__":
    test_all_vanilla()
