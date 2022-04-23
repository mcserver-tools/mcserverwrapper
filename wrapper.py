import sys
from time import sleep
from threading import Thread
import os
import os.path

from server import Server

DEFAULT_START_CMD = "java -Xmx4G -jar server.jar nogui"

class Wrapper():
    def __init__(self, args="") -> None:
        if args != "":
            self.args = args.split(" ")
        else:
            self.args = sys.argv[1::]

        # delete old logfile
        if os.path.exists("mcserverlogs.txt"):
            os.system("del mcserverlogs.txt")

        self.server = Server()
        Thread(target=self._output_reader).start()

    def startup(self):
        self._edit_properties()
        self.server.start(self._get_start_command())

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

    def _get_start_command(self):
        args = {
            "java": "java",
            "ram": "4G",
            "serverjar": "server.jar"
        }

        if "-jar" in self.args:
            index = self.args.index("-jar")
            args["serverjar"] = self.args[index + 1]
        if "-java" in self.args:
            index = self.args.index("-java")
            args["java"] = self.args[index + 1]
        if "-ram" in self.args:
            index = self.args.index("-ram")
            args["ram"] = self.args[index + 1]

        return " ".join((args["java"], "-Xmx" + args["ram"], "-jar", args["serverjar"], "nogui"))

    def _edit_properties(self):
        if not os.path.exists("./server.properties"):
            tempserver = Server()
            tempserver.start(self._get_start_command())
            tempserver.stop()

        with open("./server.properties", "r") as properties:
            lines = properties.readlines()

        if "-port" in self.args:
            for line in lines:
                if "server-port=" in line:
                    index = lines.index(line)
                    lines[index] = "server-port=" + self.args[self.args.index("-port") + 1] + "\n"
        if "-maxp" in self.args:
            for line in lines:
                if "max-players=" in line:
                    index = lines.index(line)
                    lines[index] = "max-players=" + self.args[self.args.index("-maxp") + 1] + "\n"

        with open("./server.properties", "w") as properties:
            properties.writelines(lines)

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
                    pass
            output_str = output_str.replace("\n", "")
        if output_str != "":
            for item in output_str.split("\r"):
                if item != "":
                    print(item)
            with open("mcserverlogs.txt", "a") as logfile:
                logfile.write(output_str.replace("\r", "\n"))

# teststartcommand: 
# mcserverwrapper -jar paper-1.18.2-277.jar -java java -ram 8G -port 25566 -maxp 5

# Valid arguments: 
# -java: the path to the java.exe executable (default: java)
# -jar: the server jar file (default: server.jar)
# -ram: the amount of ram the server should use (default: 4G)
# -port: the port the server should use (default: 25565)
# -maxp: the max amount of online players at the same time (default: 20)
# -whitelist: a list of banned players
