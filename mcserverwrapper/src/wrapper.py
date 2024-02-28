"""A module containing the wrapper class"""

import os
import os.path
import sys
from queue import Queue
from threading import Thread
from time import sleep

from .server import Server

DEFAULT_START_CMD = "java -Xmx4G -jar server.jar nogui"

class Wrapper():
    """The outer shell of the wrapper, handling inputs and outputs"""

    def __init__(self, command="", args=None, server_path=os.getcwd(), output=True) -> None:
        if args is None:
            args = {}

        if command != "":
            self.cmd = command
        elif len(sys.argv) == 2:
            self.cmd = sys.argv[-1]
        else:
            self.cmd = DEFAULT_START_CMD

        self.args = args
        self.server_path = server_path

        # delete old logfile
        if os.path.exists(os.path.join(self.server_path, "mcserverlogs.txt")):
            os.system(os.path.join(self.server_path, "del mcserverlogs.txt"))

        self.server = Server(self.server_path)
        if output:
            Thread(target=self._output_reader, daemon=True).start()
        else:
            self.output_queue = Queue()
            Thread(target=self._output_formatter, daemon=True).start()

    def startup(self):
        """Starts the minecraft server"""

        self._edit_properties()
        self.server.start(self.cmd, cwd=self.server_path)

    def send_command(self, command, wait_time=0):
        """Sends and executes a command on the server, then waits for the given wait_time"""

        if len(command) == 0:
            return

        self.server.execute_command(command)

        sleep(wait_time)

    def stop(self):
        """Stops the server"""

        self.server.stop()

    def server_running(self):
        """Return True if the server is pingeable"""

        return self.server.is_running()

    def _edit_properties(self):
        """Save the port and max players to the server.properites"""

        # pylint: disable=W0703

        # if the Server is started for the first time,
        # create a temp server to create the eula and server.properties
        if not os.path.isfile(os.path.join(self.server_path, "./server.properties")) or not os.path.isfile(os.path.join(self.server_path, "eula.txt")):
            tempserver = Server(self.server_path)
            try:
                tempserver.start(self.cmd, cwd=self.server_path, blocking=False)
            except Exception as exc:
                # some versions only add an empty server.properties,
                # so just add the port and max players
                if "Port couldn't be read from server.properties" in exc.args:
                    self._append_properties()
                else:
                    raise exc

            # accept the eula
            with open(os.path.join(self.server_path, "eula.txt"), "r", encoding="utf8") as file:
                lines = file.readlines()
                for index, line in enumerate(lines):
                    if line == "eula=false\n":
                        lines[index] = "eula=true\n"
            with open(os.path.join(self.server_path, "eula.txt"), "w", encoding="utf8") as file:
                file.writelines(lines)

        # pylint: enable=W0703

        # save the provided port and max players to the server.properties
        with open(os.path.join(self.server_path, "./server.properties"), "r", encoding="utf8") as properties:
            lines = properties.readlines()

        if "port" in self.args:
            for index, line in enumerate(lines):
                if "server-port=" in line:
                    lines[index] = f"server-port={self.args['port']}\n"
        if "maxp" in self.args:
            for index, line in enumerate(lines):
                if "max-players=" in line:
                    lines[index] = f"max-players={self.args['maxp']}\n"

        with open(os.path.join(self.server_path, "./server.properties"), "w", encoding="utf8") as properties:
            properties.writelines(lines)

    def _append_properties(self):
        with open(os.path.join(self.server_path, "./server.properties"), "r", encoding="utf8") as properties:
            lines = properties.readlines()
        lines.append(f"server-port={self.args['port'] if 'port' in self.args else 25565}\n")
        lines.append(f"max-players={self.args['maxp'] if 'maxp' in self.args else 20}\n")
        with open(os.path.join(self.server_path, "./server.properties"), "w", encoding="utf8") as properties:
            properties.writelines(lines)

    def _output_reader(self):
        """Print out all of the server logs"""

        for item in self.server.read_output():
            self._format_text(item, True)

    def _output_formatter(self):
        """Save all of the output lines to the queue"""

        for item in self.server.read_output():
            lines = self._format_text(item, False)
            if lines is not None:
                for line in lines:
                    if line is not None and line != "":
                        self.output_queue.put(line)

    def _format_text(self, output, printout):
        """Format the given text"""

        # try to decode the output string
        try:
            output_str = output.decode("ascii").replace("\n", "")
        # if the total decoding fails, decode every char individually
        except UnicodeDecodeError:
            output_str = ""
            for char in [output[i:i+1] for i in range(len(output))]:
                try:
                    output_str += char.decode("ascii")
                # if the conversion fails, skip the char
                except UnicodeDecodeError:
                    pass
                except AttributeError:
                    pass
            output_str = output_str.replace("\n", "")

        # ignore empty output strings to prevent empty lines
        if output_str != "":
            # in print mode, print the output string
            if printout:
                # print each line individually if it isn't empty
                for item in output_str.split("\r"):
                    if item != "":
                        print(item)
                with open(os.path.join(self.server_path, "mcserverlogs.txt"), "a", encoding="utf8") as logfile:
                    logfile.write(output_str.replace("\r", "\n"))
            # if not in print mode, return all lines as a list
            else:
                return output_str.split("\r")
        return None

# teststartcommand:
# mcserverwrapper -jar paper-1.18.2-277.jar -java java -ram 8G -port 25566 -maxp 5

# Valid arguments:
# -java: the path to the java.exe executable (default: java)
# -jar: the server jar file (default: server.jar)
# -ram: the amount of ram the server should use (default: 4G)
# -port: the port the server should use (default: 25565)
# -maxp: the max amount of online players at the same time (default: 20)
# -whitelist: a list of banned players
