from queue import Queue
import sys
from time import sleep
from pexpect import popen_spawn
from threading import Thread
import os
import os.path
import pexpect

DEFAULT_START_CMD = "java -Xmx4G -jar server.jar nogui"

class ServerWrapper():
    def __init__(self) -> None:
        # os.chdir(__file__.rsplit("\\", maxsplit=1)[0] + "\TestServer")

        # delete old logfile
        if os.path.exists("mcserverlogs.txt"):
            os.system("del mcserverlogs.txt")

        self.child = None
        self._started = False
        self._exiting = False
        self.command_queue = Queue()
        # Thread(target=self._command_executer, daemon=True).start()
        Thread(target=self._output_reader).start()

    def startup(self):
        if "-f" in sys.argv:
            index = sys.argv.index("-f")
            self.child = popen_spawn.PopenSpawn(sys.argv[index + 1], timeout=1)
        else:
            args = {
                "java": "java",
                "ram": "-Xmx4G",
                "serverjar": "server.jar"
            }
            if "-s" in sys.argv:
                index = sys.argv.index("-s")
                args["serverjar"] = sys.argv[index + 1]
            if "-j" in sys.argv:
                index = sys.argv.index("-j")
                args["java"] = sys.argv[index + 1]
            if "-r" in sys.argv:
                index = sys.argv.index("-r")
                args["ram"] = sys.argv[index + 1]
            self.child = popen_spawn.PopenSpawn(" ".join((args["java"], args["ram"], "-jar", args["serverjar"], "nogui")), timeout=1)

        # wait until the server finished starting
        while not self._started:
            sleep(1)

    def send_command(self, command, wait_time=3, print_to_console=False):
        if len(command) == 0:
            return
        if command[0] != "/":
            command = "/" + command

        if command == "/stop":
            self.stop()
        else:
            self._execute_command(command, wait_time, print_to_console)
            self._read_output()

    def stop(self):
        self._exiting = True
        self.child.sendline("/stop")
        with open("mcserverlogs.txt", "a") as logfile:
            logfile.write(("/stop\n"))

        self.child.wait()

    def _output_reader(self):
        while self.child is None:
            sleep(1)
        while not self._exiting:
            self._read_output()

    def _read_output(self):
        output = b""
        try:
            tries = 1024
            while tries > 0:
                tries -= 1
                output += self.child.read(1)
                if b"\r" in output:
                    self._format_and_print(output)
                    output = b""
                    tries = 1024
        except pexpect.exceptions.TIMEOUT:
            pass
        self._format_and_print(output)

    def _format_and_print(self, output):
        try:
            output_str = output.decode("ascii").replace("\n", "")
        except UnicodeDecodeError:
            output_str = ""
            for char in [output[i:i+1] for i in range(len(output))]:
                try:
                    output_str += char.decode("ascii")
                except UnicodeDecodeError:
                    pass
                except AttributeError:
                    print(output)
                    print(char)
                    print(type(char))
            output_str = output_str.replace("\n", "")
        if not self._started and "For help, type" in output_str:
            self._started = True
        if not self._exiting and "Stopping server" in output_str:
            self.stop()
        if output_str != "":
            for item in output_str.split("\r"):
                if item != "":
                    print(item)
            with open("mcserverlogs.txt", "a") as logfile:
                logfile.write(output_str.replace("\r", "\n"))

    def _execute_command(self, command, wait_time, print_to_console=False):
        # command, wait_time = self.command_queue.get(block=True)
        self.child.sendline(command)
        if print_to_console:
            print(command)
        with open("mcserverlogs.txt", "ab") as logfile:
            logfile.write((command + "\n").encode("ascii"))

        sleep(wait_time)

if __name__ == "__main__":
    wrapper = ServerWrapper()
    wrapper.startup()
    # wrapper.send_command("/time set day", 1, True)

    command = ""
    while command != "/stop" and not wrapper._exiting:
        command = input()
        wrapper.send_command(command)
