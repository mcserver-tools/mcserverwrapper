"""The main module showing a simple example of how to use the wrapper"""

import pathlib
import os

from mcserverwrapper.src.wrapper import Wrapper

# pylint: disable=C0103

def main():
    """Main function"""

    wrapper = Wrapper()

    try:
        wrapper.startup()

        command = ""
        while command != "/stop" and wrapper.server_running():
            command = input()
            wrapper.send_command(command, wait_time=1)
    except BaseException as e:
        wrapper.stop()
        raise e

def main2():
    """Function used for testing, don't call this!"""

    wrapper = Wrapper(os.path.join(pathlib.Path(__file__).parent.parent.resolve(),
                                               "mcserverwrapper", "test", "temp", "server.jar"),
                      print_output=True)

    try:
        wrapper.startup()
        command = ""
        while command != "/stop" and wrapper.server_running():
            command = input()
            wrapper.send_command(command, wait_time=1)
    except KeyboardInterrupt as e:
        wrapper.stop()
        raise e

if __name__ == "__main__":
    # main()
    main2()
