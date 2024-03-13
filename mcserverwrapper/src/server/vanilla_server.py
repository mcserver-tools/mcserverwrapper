"""Module containing the VanillaServer class"""

from .base_server import BaseServer
from ..mcversion import McVersionType

class VanillaServer(BaseServer):
    """Class representing a Vanilla (normal/unmodded) Minecraft server"""

    VERSION_TYPE = McVersionType.VANILLA

    def execute_command(self, command: str):
        if not command.startswith("/"):
            command = "/" + command

        super().execute_command(command)

        if command == "/stop":
            self._stopping()
