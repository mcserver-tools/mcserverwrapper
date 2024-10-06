"""The main module showing a simple example of how to use the wrapper"""

from mcserverwrapper import Wrapper

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

if __name__ == "__main__":
    main()
