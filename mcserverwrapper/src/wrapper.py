"""A module containing the wrapper class"""

import atexit
import os
import os.path
import pathlib
from queue import Queue
from threading import Thread
from time import sleep

from .util import logger

from .server import ServerBuilder
from . import server_properties_helper
from .mcversion import McVersion

class Wrapper():
    """The outer shell of the wrapper, handling inputs and outputs"""

    def __init__(self, jarfile_path: str = "server.jar", server_start_command=None, server_property_args=None,
                 print_output=True) -> None:
        self.server_jar = jarfile_path
        self.server_path = pathlib.Path(jarfile_path).parent.resolve()

        logger.setup(self.server_path)
        # delete old logfile
        logger.delete_logs()

        self._server_builder = ServerBuilder.from_jar(jarfile_path)

        prop_args_clean = server_properties_helper.parse_properties_args(self.server_path,
                                                                         server_property_args,
                                                                         self._server_builder._mcv)
        server_properties_helper.save_properties(self.server_path, prop_args_clean)
        self._server_builder.port(prop_args_clean["port"])

        if server_start_command is not None:
            self._server_builder.start_command(server_start_command)

        self.server = self._server_builder.build()
        atexit.register(self.stop)

        self.output_queue = Queue()
        Thread(target=self._t_output_handler, args=[print_output,]).start()

    def startup(self, blocking=True) -> None:
        """Starts the minecraft server"""

        # if the Server is started for the first time,
        # create a temp server to create the eula and server.properties
        if not os.path.isfile(os.path.join(self.server_path, "./server.properties")) \
           or not os.path.isfile(os.path.join(self.server_path, "eula.txt")):
            self._run_temp_server()

        # accept the eula
        # always accept eula to recover from a previous crash
        self._accept_eula()

        self.server.start(blocking=blocking)

    def send_command(self, command, wait_time=0) -> None:
        """Sends and executes a command on the server, then waits for the given wait_time"""

        if len(command) == 0:
            return

        if command == "stop":
            return

        self.server.execute_command(command)

        if wait_time > 0:
            sleep(wait_time)

    def stop(self) -> None:
        """Stops the server"""

        self.server.stop()

    def server_running(self) -> bool:
        """Return True if the server is pingeable"""

        return self.server.is_running()

    def get_version(self) -> McVersion:
        """
        Return the servers' version

        Returns:
            McVersion: The servers' version
        """

        return self.server.version

    def _run_temp_server(self):
        """Start a temporary server to generate server.properties and eula.txt"""

        tempserver = self._server_builder.build()
        atexit.register(tempserver.stop)

        try:
            tempserver.start(blocking=False)
        except ValueError:
            # some versions only add an empty server.properties,
            # so just add the port and max players later
            pass

        atexit.unregister(tempserver.stop)

    def _accept_eula(self):
        """Accept eula.txt"""

        with open(os.path.join(self.server_path, "eula.txt"), "r", encoding="utf8") as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if line == "eula=false\n":
                    lines[index] = "eula=true\n"
        with open(os.path.join(self.server_path, "eula.txt"), "w", encoding="utf8") as file:
            file.writelines(lines)

    def _t_output_handler(self, print_output=False):
        """Read all output, write to logfile and print if print_output is True"""

        for line in self.server.read_output():
            if line != "":
                logger.log(line, print_output)
                if not print_output:
                    self.output_queue.put(line)

# teststartcommand:
# mcserverwrapper -jar server.jar -java java -ram 8G -port 25566 -maxp 5

# Valid arguments:
# -java: the path to the java.exe executable (default: java)
# -jar: the server jar file (default: server.jar)
# -ram: the amount of ram the server should use (default: 4G)
# -port: the port the server should use (default: 25565)
# -maxp: the max amount of online players at the same time (default: 20)
# -whitelist: a list of banned players
