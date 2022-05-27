from queue import Queue
import sys
from time import sleep
from threading import Thread
import os
import os.path

from server import Server

DEFAULT_START_CMD = "java -Xmx4G -jar server.jar nogui"

class Wrapper():
    def __init__(self, output=True, args="") -> None:
        self._parse_args(args)

        # delete old logfile
        if os.path.exists("mcserverlogs.txt"):
            os.system("del mcserverlogs.txt")

        self.server = Server()
        if output:
            Thread(target=self._output_reader).start()
        else:
            self.output_queue = Queue()
            Thread(target=self._output_formatter).start()

    def startup(self):
        self._edit_properties()
        self.server.start(self._get_start_command())

    def send_command(self, command, wait_time=0, printout=True):
        if len(command) == 0:
            return

        self.server.execute_command(command)

        sleep(wait_time)

    def stop(self):
        self.server.stop()

    def server_running(self):
        return self.server.is_running()

    def _parse_args(self, args):
        if args != "":
            self.args = []
            temp = ""
            c = 0
            while c < len(args):
                if args[c] == '"':
                    if temp != "":
                        raise Exception(f"Invalid args: {args}")
                    temp += args[c]
                    c += 1
                    while args[c] != '"':
                        temp += args[c]
                        c += 1
                    temp += args[c]
                    self.args.append(temp)
                    temp = ""
                elif args[c] == " ":
                    self.args.append(temp)
                    temp = ""
                else:
                    temp += args[c]
                c += 1
            self.args.append(temp)
        else:
            self.args = sys.argv[1::]

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
            self._format_text(item, True)

    def _output_formatter(self):
        for item in self.server.read_output():
            lines = self._format_text(item, False)
            if lines is not None:
                for line in lines:
                    if line is not None and line != "":
                        self.output_queue.put(line)

    def _format_text(self, output, printout):
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
            if printout:
                for item in output_str.split("\r"):
                    if item != "":
                        print(item)
                with open("mcserverlogs.txt", "a") as logfile:
                    logfile.write(output_str.replace("\r", "\n"))
            else:
                return output_str.split("\r")

# teststartcommand: 
# mcserverwrapper -jar paper-1.18.2-277.jar -java java -ram 8G -port 25566 -maxp 5

# Valid arguments: 
# -java: the path to the java.exe executable (default: java)
# -jar: the server jar file (default: server.jar)
# -ram: the amount of ram the server should use (default: 4G)
# -port: the port the server should use (default: 25565)
# -maxp: the max amount of online players at the same time (default: 20)
# -whitelist: a list of banned players
