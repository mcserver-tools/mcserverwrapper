"""A module ocntining the server class"""

import os.path
import re
from threading import Thread
from time import sleep
from typing import Generator

import pexpect
from pexpect import popen_spawn

from . import info_getter

class Server():
    """The core of the wrapper, communicates directly with the minecraft servers"""

    def __init__(self, server_path: str) -> None:
        self._server_path = server_path
        self._child = None
        self._port = None
        self._version = None
        self._version_type = None

    def start(self, command, cwd=None, blocking=True):
        """Starts the minecraft server"""

        # starts the server process
        self._child = popen_spawn.PopenSpawn(cmd=command, cwd=cwd, timeout=1)

        # wait for files to get generated
        while not os.path.isfile(os.path.join(self._server_path, "./server.properties")) or not os.path.isfile(os.path.join(self._server_path, "eula.txt")):
            sleep(0.1)

        # read the port from the server.properties file
        self._read_port_from_properties()

        # if blocking is True, wait for the server to finish starting
        if blocking:
            self._wait_for_startup()
        else:
            # still call _wait_for_startup to save the version
            Thread(target=self._wait_for_startup, daemon=True).start()

    def stop(self):
        """Stop the running server"""

        self.execute_command("/stop")

    def execute_command(self, command: str):
        """Send a given command to the server"""

        # vanilla server commands must start with a '/'
        if self._version_type in ["vanilla", "snapshot"] and not command.startswith("/"):
            command = "/" + command
        # paper server commands don't start with a '/'
        elif self._version_type in ["paper", "spigot", "bukkit"] and command.startswith("/"):
            command = command[1::]

        self._child.sendline(command)

        if command == "/stop":
            while not os.access(os.path.join(self._server_path, "world", "session.lock"), os.R_OK):
                sleep(0.1)

    def is_running(self):
        """Returns True if the server responds to a ping"""

        if self._port is None:
            return False

        return info_getter.ping_address_with_return("127.0.0.1", self._port) is not None

    def read_output(self) -> Generator[str, None, None]:
        """Returns a generator which yields all outputs until the server exits"""

        # wait for the server to initialize
        while self._child is None:
            sleep(0.1)

        output = b""
        # read one char at a time, until the server exits
        while b"Stopping server" not in output:
            try:
                output += bytes(self._child.read(1))
                # if a line break is in the output, return line
                if b"\r" in output:
                    yield self._format_output(output)
                    output = b""
            # Exception Normal: on timeout retry until a new char can be read
            except pexpect.exceptions.TIMEOUT:
                pass
        yield self._format_output(output)

        output = b""
        empties = 0
        while True:
            try:
                char = self._child.read(1)
                if char == b"":
                    empties += 1
                else:
                    empties = 0
                output += char
                # if a line break is in the output, return line
                if b"\r" in output:
                    yield self._format_output(output)
                    output = b""
                # if more than 10 empty chars have been read, all data has been read
                if empties >= 10:
                    return self._format_output(output)
            # Exception Normal: on timeout retry until a new char can be read
            except pexpect.exceptions.TIMEOUT:
                pass
            # If the End of File is read, all data has been read
            except pexpect.exceptions.EOF:
                return self._format_output(output)

    def _read_port_from_properties(self):
        """Reads and stores the port from the server.properties file"""

        with open(os.path.join(self._server_path, "server.properties"), "r", encoding="utf8") as properties_file:
            lines = properties_file.read().splitlines()
        for line in lines:
            if "server-port" in line:
                if line.split("=")[1].isdecimal():
                    self._port = int(line.split("=")[1])
        if self._port is None:
            raise ValueError("Port couldn't be read from server.properties")

    def _wait_for_startup(self):
        """Waits for the server to finish starting and then stores its version"""

        response = info_getter.ping_address_with_return("127.0.0.1", self._port)
        while response is None:
            sleep(1)
            response = info_getter.ping_address_with_return("127.0.0.1", self._port)

        self._parse_and_save_version_string(response.version.name)

    def _format_output(self, raw_text: bytes) -> str:
        # remove line breaks
        raw_text = raw_text.replace(b"\r", b"").replace(b"\n", b"")

        # try to decode the output string
        try:
            text_str = raw_text.decode("ascii").replace("\n", "")
        # if the total decoding fails, decode every char individually
        except UnicodeDecodeError:
            text_str = ""
            for char in [raw_text[i:i+1] for i in range(len(raw_text))]:
                try:
                    text_str += char.decode("ascii")
                # if the conversion fails, skip the char
                except UnicodeDecodeError:
                    pass
                except AttributeError:
                    pass
            text_str = text_str.replace("\n", "")

        return text_str

    def _parse_and_save_version_string(self, version_raw):
        """Search the given version string to find out the version type"""

        self._version = version_raw

        if re.search(r"^1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
            self._version_type = "vanilla"
        elif re.search(r"^[1-2][0-9]w[0-9]{1,2}[a-z]", version_raw) is not None:
            self._version_type = "snapshot"
        elif re.search(r"^Paper 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
            self._version_type = "paper"
        elif re.search(r"^PaperSpigot 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
            self._version_type = "paper"
        elif re.search(r"^Spigot 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
            self._version_type = "spigot"
        elif re.search(r"^CraftBukkit 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
            self._version_type = "bukkit"
        else:
            self._version_type = "unknown"
