from wrapper import Wrapper

if __name__ == "__main__":
    wrapper = Wrapper()
    wrapper.startup()

    command = ""
    while command != "/stop" and wrapper.server_running():
        command = input()
        wrapper.send_command(command, printout=False)
