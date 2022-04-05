import sys
from time import sleep
from pexpect import popen_spawn
from threading import Thread
import os
import os.path
import pexpect

from server import Server

DEFAULT_START_CMD = "java -Xmx4G -jar server.jar nogui"

class Wrapper():
    def __init__(self) -> None:
        # delete old logfile
        if os.path.exists("mcserverlogs.txt"):
            os.system("del mcserverlogs.txt")

        self.server = Server()
        Thread(target=self._output_reader).start()

    def startup(self):
        if "-f" in sys.argv:
            index = sys.argv.index("-f")
            self.server.start(sys.argv[index + 1])
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
            self.server.start(" ".join((args["java"], args["ram"], "-jar", args["serverjar"], "nogui")))

    def send_command(self, command, wait_time=0, printout=True):
        if len(command) == 0:
            return

        self.server.execute_command(command)
        if printout:
            print(command)
        with open("mcserverlogs.txt", "a") as logfile:
            logfile.write((command + "\n"))

        sleep(wait_time)

    def stop(self):
        self.server.stop()

    def server_running(self):
        return self.server.is_running()

    def _output_reader(self):
        for item in self.server.read_output():
            self._format_and_print(item)

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
                    # print(output)
                    # print(char)
                    # print(type(char))
                    pass
            output_str = output_str.replace("\n", "")
        if output_str != "":
            for item in output_str.split("\r"):
                if item != "":
                    print(item)
            with open("mcserverlogs.txt", "a") as logfile:
                logfile.write(output_str.replace("\r", "\n"))
