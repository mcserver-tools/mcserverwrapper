from datetime import datetime, timedelta
from time import sleep
import pexpect
from pexpect import popen_spawn
import os.path
import re

import info_getter

class Server():
    def __init__(self) -> None:
        self._child = None
        self._port = None
        self._version = None
        self._version_type = None

    def start(self, command):
        self._child = popen_spawn.PopenSpawn(command, timeout=1)

        while not os.path.exists("server.properties"):
            sleep(1)

        with open("server.properties", "r") as properties:
            lines = properties.readlines()
            for line in lines:
                if line.split("=")[0] == "server-port":
                    self._port = int(line.split("=")[1])

        while info_getter.ping_address_with_return("127.0.0.1", self._port) == None:
            sleep(1)

        self._format_version(info_getter.ping_address_with_return("127.0.0.1", self._port).version.name)

    def stop(self):
        if self._version_type in ["vanilla", "snapshot"]:
            self.execute_command("/stop")
        elif self._version_type in ["paper", "spigot", "bukkit"]:
            self.execute_command("stop")

    def execute_command(self, command):
        if self._version_type in ["vanilla", "snapshot"] and command[0] != "/":
            command = "/" + command
        elif self._version_type in ["paper", "spigot", "bukkit"] and command[0] == "/":
            command = command[1::]

        self._child.sendline(command)

    def is_running(self):
        if self._port is None:
            return False
        return info_getter.ping_address_with_return("127.0.0.1", self._port) is not None

    def read_output(self):
        output = b""

        while self._child is None:
            sleep(1)

        while b"Stopping server" not in output:
            try:
                output += self._child.read(1)
                if b"\r" in output:
                    yield output
                    output = b""
            except pexpect.exceptions.TIMEOUT:
                pass
        yield output

        try:
            output = b""
            start_time = datetime.now()
            while (datetime.now() - start_time) < timedelta(seconds=5):
                output += self._child.read(1)
                if b"\r" in output:
                    yield output
                    output = b""
        except pexpect.exceptions.TIMEOUT:
            pass
        yield output
        yield self._child.read(-1)

    def _format_version(self, version_raw):
            self._version = version_raw

            if re.search("^1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
                self._version_type = "vanilla"
            elif re.search("^[1-2][0-9]w[0-9]{1,2}[a-z]", version_raw) is not None:
                self._version_type = "snapshot"
            elif re.search("^Paper 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
                self._version_type = "paper"
            elif re.search("^PaperSpigot 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
                self._version_type = "paper"
            elif re.search("^Spigot 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
                self._version_type = "spigot"
            elif re.search("^CraftBukkit 1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", version_raw) is not None:
                self._version_type = "bukkit"
            else:
                self._version_type = "unknown"
