"""Module containing the VanillaServer class"""

from __future__ import annotations

import json
import os
import re
from zipfile import ZipFile
from .base_server import BaseServer
from ..mcversion import McVersion, McVersionType

class VanillaServer(BaseServer):
    """Class representing a Vanilla (normal/unmodded) Minecraft server"""

    VERSION_TYPE = McVersionType.VANILLA

    def execute_command(self, command: str):
        if not command.startswith("/"):
            command = "/" + command

        super().execute_command(command)

        if command == "/stop":
            self._stopping()

    @classmethod
    def _check_jar(cls, jar_file: str) -> McVersion | None:
        """Search the given jar file to find the version"""

        with ZipFile(jar_file, "r") as zf:
            # for Minecraft 1.14+
            version_json = None
            for zip_fileinfo in zf.filelist:
                if zip_fileinfo.filename == "version.json":
                    version_json = json.loads(zf.read(zip_fileinfo))
            if version_json is not None:
                return McVersion(version_json["name"], cls.VERSION_TYPE)

            # for Mineraft 1.13.2-
            mcs_class = None
            for zip_fileinfo in zf.filelist:
                if zip_fileinfo.filename == "net/minecraft/server/MinecraftServer.class":
                    mcs_class = zf.read(zip_fileinfo)
            if mcs_class is not None:
                vers = [x.group() for x in re.finditer(r"1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?",
                                                       mcs_class.decode("utf8", errors="ignore"))]
                if len(vers) != 0:
                    return McVersion(vers[0], cls.VERSION_TYPE)

        # no version was found
        return None

    @classmethod
    def _check_jar_name(cls, jar_file: str) -> McVersion | None:
        """Search the name of the given jar file to find the version"""

        jar_filename = jar_file.rsplit(os.sep, maxsplit=1)[1]

        # vanilla server jars are usually just 'server.jar', which doesn't help here
        if jar_filename == "server.jar":
            return None

        if re.search(r"^minecraft_server\.1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?\.jar", jar_filename) is not None:
            vers = [x.group() for x in re.finditer(r"^minecraft_server\.1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?\.jar",
                                                   jar_filename)]
            return McVersion(vers[0].replace("minecraft_server.", "").replace(".jar", ""), cls.VERSION_TYPE)

        # no version was found
        return None
