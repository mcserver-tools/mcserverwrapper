"""The main module showing a simple example of how to use the wrapper"""

import pathlib
import os
from time import sleep

from mcserverwrapper.src.wrapper import Wrapper

# pylint: disable=C0103

def main():
    wrapper = Wrapper()
    wrapper.startup()

    command = ""
    while command != "/stop" and wrapper.server_running():
        command = input()
        wrapper.send_command(command, wait_time=1)

def main2():
    wrapper = Wrapper(server_path=os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "mcserverwrapper", "test", "temp"), print_output=True)
    wrapper.startup()

    command = ""
    while command != "/stop" and wrapper.server_running():
        command = input()
        wrapper.send_command(command, wait_time=1)

if __name__ == "__main__":
    main()
    # main2()
