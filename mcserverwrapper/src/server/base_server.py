"""A module contining the base server class"""

from __future__ import annotations

import os.path
import re
import signal
import sys
from datetime import datetime, timedelta
from subprocess import TimeoutExpired
from time import sleep
from typing import Generator

import pexpect
from pexpect import popen_spawn

from ..mcversion import McVersion
from ..util import info_getter, logger
from ..error import ServerExitedError

class BaseServer:
    """The base server, containing server type-independent functionality"""

    def __init__(self, server_path: str, version: McVersion, port: int, start_cmd: str) -> None:
        self.server_path = server_path
        self.version = version
        self._port = port
        self._start_cmd = start_cmd
        self._child = None

    VERSION_TYPE = None

    def start(self, blocking=True):
        """Starts the minecraft server"""

        # starts the server process
        self._child = popen_spawn.PopenSpawn(cmd=self._start_cmd, cwd=self.server_path, timeout=1)

        # wait for files to get generated or server to exit
        while (not os.path.isfile(os.path.join(self.server_path, "./server.properties")) \
               or not os.path.isfile(os.path.join(self.server_path, "eula.txt"))
              and self.get_child_status(0.1) is None):
            sleep(0.1)

        # check if server crashed
        if self.get_child_status(0.1) not in [None, 0]:
            raise ServerExitedError(f"Server unexpectedly exited with exit code {self.get_child_status(0.1)}")

        # if blocking is True, wait for the server to finish starting
        if blocking:
            self._wait_for_startup()

    def stop(self):
        """Stop the running server gracefully, and kills it if it doesn't stop within 20 seconds"""

        # server hasn't yet started, so it doesn't need to be stopped
        if self._child is None:
            return

        if self.get_child_status(1) is None:
            self.execute_command("/stop")

    def kill(self):
        """Kill the server process, but UNSAVED DATA WILL BE LOST AND SAVES POSSIBLY CORRUPTED"""

        logger.log("Killing server process")
        if sys.platform == "win32":
            os.system(f"taskkill /pid {self._child.pid} /f")
        else:
            self._child.kill(signal.SIGKILL)
        
        if self.get_child_status(30) is None:
            logger.log("Server did not stop")
            logger.log("We're running out of options, maybe try manually killing the server?")

    def execute_command(self, command: str) -> None:
        """Send a given command to the server"""

        logger.log(f"Sending command: {command}")
        self._child.sendline(command)

    def get_child_status(self, timeout: int) -> int | None:
        """
        Return the exit status of the server process, or None if the process is still alive after the timeout
        @param timeout: the amount of seconds to wait for the process to exit
        """

        try:
            status = self._child.proc.wait(timeout)
            # server stopped
            return status
        except TimeoutExpired:
            # expected exception, server is still running
            return None

    def is_running(self):
        """Returns True if the server responds to a ping"""

        if self._port is None:
            return False

        return info_getter.ping_address_with_return("127.0.0.1", self._port) is not None

    def read_output(self, timeout=None) -> Generator[str, None, None]:
        """Returns a generator which yields all outputs until the server exits"""

        if timeout is None:
            terminate_time = datetime.max
        else:
            terminate_time = datetime.now() + timedelta(seconds=timeout)
            if not isinstance(timeout, (int, float)):
                raise TypeError(f"timeout expected type (int, float), not {type(timeout)}")

        # wait for the server to initialize
        while self._child is None:
            sleep(0.1)

        output = b""
        empties = 0
        # read one char at a time, until the server exits
        while terminate_time > datetime.now():
            try:
                output_char = bytes(self._child.read(1))

                if output == b"":
                    empties += 1
                else:
                    empties = 0

                output += output_char

                # if a line break is in the output, return line
                if b"\n" in output:
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

        return ""

    def _wait_for_startup(self):
        """Waits for the server to finish starting and then stores its version"""

        response = None
        while response is None and self.get_child_status(1) is None:
            response = info_getter.ping_address_with_return("127.0.0.1", self._port)
            sleep(1)

    def _ensure_stop(self):
        logger.log("Stopping server")
        status = self.get_child_status(30)
        if status is None:
            logger.log("Server did not stop within 30 seconds")
            if sys.platform == "win32":
                self._child.kill(signal.CTRL_C_EVENT)
            else:
                self._child.kill(signal.SIGTERM)

            status = self.get_child_status(60)
            if status is None:
                logger.log("Server did not stop within 90 seconds")

    def _format_output(self, raw_text: bytes) -> str:
        # remove line breaks
        raw_text = raw_text.replace(b"\r", b"").replace(b"\n", b"")

        # try to decode the output string
        try:
            text_str = raw_text.decode("ascii")
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

        return text_str

    # pylint: disable=attribute-defined-outside-init, unreachable, protected-access, undefined-variable
    @staticmethod
    def _check_jar(jar_file: str) -> McVersion | None:
        """Search the given jar file to find the version"""

        raise NotImplementedError()

        filename = jar_file.rsplit(".", maxsplit=1)[0]
        version_type = None
        version = None

        if re.search(r"^1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", filename) is not None:
            self._version_type = "vanilla"
        elif re.search(r"^[1-2][0-9]w[0-9]{1,2}[a-z]", filename) is not None:
            self._version_type = "snapshot"
        elif re.search(r"^Paper 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", filename) is not None:
            self._version_type = "paper"
        elif re.search(r"^PaperSpigot 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", filename) is not None:
            self._version_type = "paper"
        elif re.search(r"^Spigot 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", filename) is not None:
            self._version_type = "spigot"
        elif re.search(r"^CraftBukkit 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", filename) is not None:
            self._version_type = "bukkit"
        else:
            self._version_type = "unknown"
    # pylint: enable=attribute-defined-outside-init, unreachable, protected-access, undefined-variable

    @staticmethod
    def _check_jar_name(jar_file: str) -> McVersion | None:
        """Search the name of the given jar file to find the version"""

        raise NotImplementedError()
