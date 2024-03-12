from .base_server import BaseServer
from ..mcversion import McVersion, McVersionType

class PaperServer(BaseServer):
    VERSION_TYPE = McVersionType.PAPER

    def execute_command(self, command: str):
        if command.startswith("/"):
            command = command[1::]

        ret = super().execute_command(command)

        if command == "stop":
            self._stopping()
        
        return ret
