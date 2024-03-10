"""A module ocntining the server class"""

from __future__ import annotations

import _thread
import os.path
import re
from datetime import datetime, timedelta
from subprocess import TimeoutExpired
from threading import Thread
from time import sleep
from typing import Generator

import pexpect
from pexpect import popen_spawn

from . import info_getter, logger

class Server():
    """The core of the wrapper, communicates directly with the minecraft servers"""

    def __init__(self, server_path: str, exit_program_on_error=False) -> None:
        self._server_path = server_path
        self._child = None
        self._port = None
        self._version = None
        self._version_type = None
        self._watchdog = Thread(target=self._t_watchdog, args=[exit_program_on_error,], daemon=True)

    def start(self, command, cwd=None, blocking=True):
        """Starts the minecraft server"""

        # starts the server process
        self._child = popen_spawn.PopenSpawn(cmd=command, cwd=cwd, timeout=1)

        # starts the server watchdog
        self._watchdog.start()

        # wait for files to get generated or server to exit
        while (not os.path.isfile(os.path.join(self._server_path, "./server.properties")) \
               or not os.path.isfile(os.path.join(self._server_path, "eula.txt"))):
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
            sleep(1)

    def get_child_status(self, timeout: int) -> int | None:
        """Return the exit status of the server process, or None if the process is still alive"""

        try:
            status = self._child.proc.wait(timeout)
            # server stopped
            return status
        except TimeoutExpired:
            # expected exception, server is running correctly
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

    def _t_watchdog(self, exit_program_on_error):
        has_started = False
        ping_timeouts = 0
        exit_watchdog = False

        while not exit_watchdog:
            if not has_started:
                status = self.get_child_status(1)

                # server startup failed
                if status is not None:
                    # exit watchdog on status 0, this means that the eula is not accepted
                    if status == 0:
                        exit_watchdog = True
                    else:
                        self._t_exit(exit_program_on_error)
                        return
                has_started = self.is_running()

            if False and has_started and not self.is_running(): # pylint: disable=R1727
                if ping_timeouts > 5:
                    # return self._t_exit(exit_program_on_error)
                    pass
                else:
                    ping_timeouts += 1
                    logger.log(f"server ping timed out {ping_timeouts} in a row")
                    sleep(5)
            else:
                ping_timeouts = 0

    def _t_exit(self, exit_program_on_error):
        sleep(3)
        for line in self.read_output(3):
            logger.log(line)
        logger.log("Server has crashed, exiting...")
        if exit_program_on_error:
            os._exit(1)
        else:
            _thread.interrupt_main()
