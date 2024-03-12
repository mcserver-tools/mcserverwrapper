import json
import pathlib
import os
from zipfile import ZipFile

from .base_server import BaseServer
from .vanilla_server import VanillaServer
from ..mcversion import McVersion, McVersionType
from ..util import logger

class ServerBuilder:
    """Builder clas to create a new Server object"""

    __create_key = object()

    @classmethod
    def from_jar(cls, jar_file: str):
        if not isinstance(jar_file, str):
            raise TypeError(f"Expected str, got {type(jar_file)}")

        if not os.path.isfile(jar_file):
            raise FileNotFoundError(f"Jarfile {jar_file} not found")
        if not jar_file.endswith(".jar"):
            raise FileNotFoundError("Expected a .jar file")

        mcv = ServerBuilder._check_jar(jar_file)
        assert isinstance(mcv, McVersion)

        server_path = pathlib.Path(jar_file).parent.resolve()

        server = None
        match mcv.type:
            case McVersionType.VANILLA:
                server = VanillaServer(server_path, mcv)
        
        assert server is not None
        
        builder = ServerBuilder(cls.__create_key, server)
        return builder
    
    def build(self):
        assert isinstance(self._server, BaseServer)
        return self._server

    def __init__(self, create_key, server: BaseServer) -> None:
        if create_key != ServerBuilder.__create_key:
            raise NotImplementedError("Cannot instantiate builder class")

        self._server = server

    @staticmethod
    def _check_jar(jar_file: str) -> McVersion:
        mcv = None

        mcv = ServerBuilder._check_jar_fabric(jar_file)
        if mcv is not None:
            return mcv
        
        mcv = ServerBuilder._check_jar_vanilla(jar_file)
        if mcv is not None:
            return mcv
        
        raise ValueError(f"Minecraft version could not be identified from {jar_file}")

    @staticmethod
    def _check_jar_fabric(jar_file: str) -> McVersion | None:
        return None

    @staticmethod
    def _check_jar_vanilla(jar_file: str) -> McVersion | None:
        version_json = None
        with ZipFile(jar_file, "r") as zf:
            for zip_fileinfo in zf.filelist:
                if zip_fileinfo.filename == "version.json":
                    version_json = json.loads(zf.read(zip_fileinfo))
        if version_json is None:
            return None
        return McVersion(version_json["name"], McVersionType.VANILLA)
