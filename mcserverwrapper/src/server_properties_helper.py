"""Module providing methods for managing the server.properties"""

from __future__ import annotations

import os
import re
from typing import Any

from .mcversion import McVersion

DEFAULT_PORT = 25565
DEFAULT_MAX_PLAYERS = 20
DEFAULT_ONLINE_MODE = "true"
DEFAULT_LEVEL_TYPE_PRE_1_19 = "default"
DEFAULT_LEVEL_TYPE_1_19 = "minecraft\\:normal"

ALL_PROPERTIES = [
    "port",
    "maxp",
    "onli",
    "levt"
]

# how many different property args are allowed
PROPERTY_ARGS_COUNT = len(ALL_PROPERTIES)

def get_properties(server_path: str, server_version: McVersion) -> dict[str, Any]:
    """Return the currently stored properties"""

    return parse_properties_args(server_path, None, server_version)

def parse_properties_args(server_path: str, server_property_args: dict | None, server_version: McVersion) \
                          -> dict[str, Any]:
    """Parse the given server_properties_args and provide defaults for missing values"""

    if server_property_args is None:
        server_property_args = {}
    else:
        server_property_args = server_property_args.copy()

    # use values from server.properties if it exists
    props_path = os.path.join(server_path, "server.properties")
    if os.path.isfile(props_path):
        with open(props_path, "r", encoding="utf8") as props_file:
            lines = props_file.read().splitlines()

        for line in lines:
            if "port" not in server_property_args:
                if "server-port=" in line:
                    port_string = line.split("=")[1]
                    if port_string.isdecimal():
                        server_property_args["port"] = int(port_string)
            if "maxp" not in server_property_args:
                if "max-players=" in line:
                    maxp_string = line.split("=")[1]
                    if maxp_string.isdecimal():
                        server_property_args["maxp"] = int(maxp_string)
            if "onli" not in server_property_args:
                if "online-mode=" in line:
                    server_property_args["onli"] = line.split("=")[1]
            if "levt" not in server_property_args:
                if "level-type=" in line:
                    server_property_args["levt"] = line.split("=")[1]

    # fall back to default values
    if "port" not in server_property_args:
        server_property_args["port"] = DEFAULT_PORT
    if "maxp" not in server_property_args:
        server_property_args["maxp"] = DEFAULT_MAX_PLAYERS
    if "onli" not in server_property_args:
        server_property_args["onli"] = DEFAULT_ONLINE_MODE
    if "levt" not in server_property_args:
        if server_version.id < McVersion.version_name_to_id("1.19"):
            server_property_args["levt"] = DEFAULT_LEVEL_TYPE_PRE_1_19
        else:
            server_property_args["levt"] = DEFAULT_LEVEL_TYPE_1_19

    # set default level type to the correct version
    if server_version.id < McVersion.version_name_to_id("1.19"):
        if server_property_args["levt"] == DEFAULT_LEVEL_TYPE_1_19:
            server_property_args["levt"] = DEFAULT_LEVEL_TYPE_PRE_1_19
        elif re.search(r"^minecraft\\\:*", server_property_args["levt"]) is not None:
            server_property_args["levt"] = server_property_args["levt"].replace("minecraft\\:", "")

    if server_version.id >= McVersion.version_name_to_id("1.19"):
        if server_property_args["levt"] == DEFAULT_LEVEL_TYPE_PRE_1_19:
            server_property_args["levt"] = DEFAULT_LEVEL_TYPE_1_19
        elif re.search(r"^minecraft\\\:*", server_property_args["levt"]) is None:
            server_property_args["levt"] = "minecraft\\:" + server_property_args["levt"]

    return server_property_args

def save_properties(server_path: str, server_property_args: dict[str, Any]) -> None:
    """Save all values from server_property_args to server.properties"""

    _validate_property_args(server_property_args)

    props_path = os.path.join(server_path, "server.properties")
    if not os.path.isfile(props_path):
        # create empty file
        with open(props_path, "w+", encoding="utf8"):
            pass

    with open(props_path, "r", encoding="utf8") as properties:
        lines = properties.readlines()

    # update existing props
    missing_props = ALL_PROPERTIES.copy()
    for index, line in enumerate(lines):
        if "server-port=" in line:
            lines[index] = f"server-port={server_property_args['port']}\n"
            missing_props.remove("port")
        if "max-players=" in line:
            lines[index] = f"max-players={server_property_args['maxp']}\n"
            missing_props.remove("maxp")
        if "online-mode=" in line:
            lines[index] = f"online-mode={server_property_args['onli']}\n"
            missing_props.remove("onli")
        if "level-type=" in line:
            lines[index] = f"level-type={server_property_args['levt']}\n"
            missing_props.remove("levt")

    # add missing properties
    if "port" in missing_props:
        lines.append(f"server-port={server_property_args['port']}\n")
    if "maxp" in missing_props:
        lines.append(f"max-players={server_property_args['maxp']}\n")
    if "onli" in missing_props:
        lines.append(f"online-mode={server_property_args['onli']}\n")
    if "levt" in missing_props:
        lines.append(f"level-type={server_property_args["levt"]}\n")

    with open(props_path, "w", encoding="utf8") as properties:
        properties.writelines(lines)

def _validate_property_args(server_property_args: dict[str, Any]):
    if server_property_args is None or not isinstance(server_property_args, dict):
        raise TypeError(f"Invalid type {type(server_property_args)} for server_property_args")
    if len(server_property_args) != PROPERTY_ARGS_COUNT:
        raise ValueError(f"Incorrect length of elements '{len(server_property_args)}'" + \
                         f" for server_property_args, expected '{PROPERTY_ARGS_COUNT}'")

    required_keys = ALL_PROPERTIES.copy()
    for k in required_keys:
        if not k in server_property_args:
            raise KeyError(f"Missing key '{k}' in server_property_property_args")
    for item in server_property_args:
        if item not in required_keys:
            raise KeyError(f"Unexpected key '{k}' in server_property_property_args")
