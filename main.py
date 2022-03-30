from queue import Queue
import subprocess
from time import sleep
from pexpect import popen_spawn
from threading import Thread
import os
import os.path
import pexpect

class ServerWrapper():
    def __init__(self) -> None:
        os.chdir(os.getcwd() + "\TestServer")

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
        # f = open("mcserverlogs.txt", "ab")
        self.child = popen_spawn.PopenSpawn("java -Xmx2G -jar server.jar nogui", timeout=1)

        # wait until the server finished starting
        while not self._started:
            sleep(1)

    def send_command(self, command, wait_time=5, print_to_console=False):
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
        while not self._exiting:
            if self.child is not None:
                self._read_output()
            else:
                sleep(1)

    def _read_output(self):
        output = b""
        try:
            tries = 10000
            while tries > 0:
                tries -= 1
                output += self.child.read(10)
        except pexpect.exceptions.TIMEOUT:
            try:
                tries = 10000
                while tries > 0:
                    tries -= 1
                    read = self.child.read(1)
                    if read == "":
                        break
                    else:
                        output += read
            except pexpect.exceptions.TIMEOUT:
                pass

        output = output.decode("ascii").replace("\n", "")
        if not self._started and "For help, type" in output:
            self._started = True
        if output != "":
            for item in output.split("\r"):
                if item != "":
                    print(item)
            with open("mcserverlogs.txt", "a") as logfile:
                logfile.write(output.replace("\r", "\n"))

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
    wrapper.send_command("/time set day", 1, True)
    wrapper.send_command("/time set night", 1, True)

    command = ""
    while command != "/stop":
        command = input()
        wrapper.send_command(command)
