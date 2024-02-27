"""The main module showing a simple example of how to use the wrapper"""

import os
from time import sleep

from wrapper import Wrapper

# pylint: disable=C0103

if __name__ == "__main__":
    wrapper = Wrapper()
    wrapper.startup()

    command = ""
    while command != "/stop" and wrapper.server_running():
        command = input()
        wrapper.send_command(command, wait_time=1)
    sleep(10)
