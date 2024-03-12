from .base_server import BaseServer
from ..mcversion import McVersion, McVersionType

class VanillaServer(BaseServer):
    VERSION_TYPE = McVersionType.VANILLA

    def execute_command(self, command: str):
        if not command.startswith("/"):
            command = "/" + command

        ret = super().execute_command(command)

        if command == "/stop":
            self._stopping()
        
        return ret
