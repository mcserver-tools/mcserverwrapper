"""Module containing the PaperServer class"""

from .base_server import BaseServer
from ..mcversion import McVersionType

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