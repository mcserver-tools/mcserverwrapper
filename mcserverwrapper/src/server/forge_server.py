"""Module containing the ForgeServer class"""

from __future__ import annotations

import json
import os
import re
from zipfile import ZipFile
from .base_server import BaseServer
from ..mcversion import McVersion, McVersionType

class ForgeServer(BaseServer):
    """
    Class representing a Forge server
    More info about Forge: https://minecraftforge.net/
    """

    VERSION_TYPE = McVersionType.FORGE

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
                # regex for old forge versions
                pattern = r"^1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?\-[fF]orge"
                if re.search(pattern, version_json["id"]) is not None:
                    vers = [x.group() for x in re.finditer(pattern, version_json["id"])]
                    return McVersion(vers[0].split("-", maxsplit=1)[0], cls.VERSION_TYPE)

        # no version was found
        return None

    @classmethod
    def _check_jar_name(cls, jar_file: str) -> McVersion | None:
        """Search the name of the given jar file to find the version"""

        jar_filename = jar_file.rsplit(os.sep, maxsplit=1)[1]

        # common filename pattern
        pattern = r"^forge-1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?\-.*.jar$"
        if re.search(pattern, jar_filename) is not None:
            vers = [x.group() for x in re.finditer(pattern, jar_filename)]
            return McVersion(vers[0].split("-", maxsplit=2)[1], cls.VERSION_TYPE)

        # no version was found
        return None
