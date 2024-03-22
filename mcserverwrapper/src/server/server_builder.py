"""Module containing the ServerBuilder class which is used to create server instances"""

from __future__ import annotations

import os
from pathlib import Path

from mcserverwrapper.src.util import logger

from .base_server import BaseServer
from .vanilla_server import VanillaServer
from .forge_server import ForgeServer
from ..mcversion import McVersion, McVersionType

DEFAULT_START_CMD = "java -Xmx4G -Xms4G -jar server.jar nogui"

class ServerBuilder:
    """
    Builder class to create a new Server object
    Constructor scheme from https://stackoverflow.com/a/46459300/15436169
    """

    __create_key = object()

    SERVER_CLASSES: dict[int, type[BaseServer]] = {
        McVersionType.FORGE: ForgeServer,
        McVersionType.VANILLA: VanillaServer # !!! VanillaServer has to be the last element !!!
    }

    @classmethod
    def from_jar(cls, jar_file: str) -> ServerBuilder:
        """
        Construct a new ServerBuilder from a server jar

        Args:
            jar_file (str): the full or relative path to the jar file to be used to start the server
        
        Returns:
            ServerBuilder: a new ServerBuilder instance
        """

        if not isinstance(jar_file, str):
            raise TypeError(f"Expected str, got {type(jar_file)}")

        if not os.path.isfile(jar_file):
            raise FileNotFoundError(f"Jarfile {jar_file} not found")
        if not jar_file.endswith(".jar"):
            raise FileNotFoundError("Expected a .jar file")

        mcv = ServerBuilder._check_jar(jar_file)
        assert isinstance(mcv, McVersion)

        builder = ServerBuilder(cls.__create_key, jar_file, mcv)

        return builder

    def start_command(self, start_command: str) -> ServerBuilder:
        """
        Add a custom start command to the server

        Args:
            start_command (str): the command to be used to start the server

        Returns:
            ServerBuilder: the same ServerBuilder instance
        """

        if not isinstance(start_command, str):
            raise TypeError(f"Expected str, got {type(start_command)}")

        self._start_cmd = start_command
        return self

    def port(self, port: int) -> ServerBuilder:
        """
        Set the server port, which is used to check if the server actually has fully started

        Args:
            port (int): the port to be used for server status checks

        Returns:
            ServerBuilder: the same ServerBuilder instance
        """

        if not isinstance(port, int):
            raise TypeError(f"Expected int, got {type(port)}")

        self._port = port
        return self

    def build(self) -> BaseServer:
        """
        Build the actual server instance
        This method can be called multiple times

        Returns:
            BaseServer: The new server instance which is a superclass of BaseServer
        """

        server_path = Path(self._jar_path).parent.resolve()

        clazz = self.SERVER_CLASSES[self._mcv.type]
        server = clazz(server_path, self._mcv, self._port, self._start_cmd)

        assert server is not None
        return server

    def __init__(self, create_key, jar_path: str, mcv: McVersion) -> None:
        if create_key != ServerBuilder.__create_key:
            raise NotImplementedError("Cannot instantiate builder class, call from_jar instead")

        self._jar_path = jar_path
        self._mcv = mcv
        self._start_cmd = DEFAULT_START_CMD.replace("server.jar", Path(jar_path).name)
        self._port = None

    # pylint: disable=protected-access
    @classmethod
    def _check_jar(cls, jar_file: str) -> McVersion:
        mcv = None

        for clazz in cls.SERVER_CLASSES.values():
            mcv = clazz._check_jar(jar_file)
            if mcv is not None:
                logger.log(f"Detected Minecraft version: {mcv}")
                return mcv

        logger.log(f"Minecraft version could not be read from {jar_file.rsplit(os.sep, maxsplit=1)[1]}," + \
                   " checking filename")

        for clazz in cls.SERVER_CLASSES.values():
            mcv = clazz._check_jar_name(jar_file)
            if mcv is not None:
                logger.log(f"Detected Minecraft version: {mcv}")
                return mcv

        raise ValueError(f"Minecraft version could not be identified from {jar_file.rsplit(os.sep, maxsplit=1)[1]}")
    # pylint: enable=protected-access
