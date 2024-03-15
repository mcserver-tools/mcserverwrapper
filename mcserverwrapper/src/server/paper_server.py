"""Module containing the PaperServer class"""

from __future__ import annotations

from .base_server import BaseServer
from ..mcversion import McVersion, McVersionType

class PaperServer(BaseServer):
    """
    Class representing a Paper server
    More info about paper: https://papermc.io/
    """

    VERSION_TYPE = McVersionType.PAPER

    def execute_command(self, command: str):
        if command.startswith("/"):
            command = command[1::]

        super().execute_command(command)

        if command == "stop":
            self._stopping()

    @staticmethod
    def _check_jar(jar_file: str) -> McVersion | None:
        """Search the given jar file to find the version"""

        raise NotImplementedError()

    @staticmethod
    def _check_jar_name(jar_file: str) -> McVersion | None:
        """Search the name of the given jar file to find the version"""

        raise NotImplementedError()
