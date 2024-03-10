"""Module providing methods for managing the server.properties"""

import os
from typing import Any

# how many different property args are allowed
PROPERTY_ARGS_COUNT = 3

DEFAULT_PORT = 25565
DEFAULT_MAX_PLAYERS = 20
DEFAULT_ONLINE_MODE = "true"

def parse_properties_args(server_path: str, server_property_args: dict | None) -> dict[str, Any]:
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

        if "port" not in server_property_args:
            for line in lines:
                if "server-port=" in line:
                    port_string = line.split("=")[1]
                    if port_string.isdecimal():
                        server_property_args["port"] = int(port_string)

        if "maxp" not in server_property_args:
            for line in lines:
                if "max-players=" in line:
                    maxp_string = line.split("=")[1]
                    if maxp_string.isdecimal():
                        server_property_args["maxp"] = int(maxp_string)

        if "onli" not in server_property_args:
            for line in lines:
                if "online-mode=" in line:
                    server_property_args["onli"] = line.split("=")[1]

    # fall back to default values
    if "port" not in server_property_args:
        server_property_args["port"] = DEFAULT_PORT
    if "maxp" not in server_property_args:
        server_property_args["maxp"] = DEFAULT_MAX_PLAYERS
    if "onli" not in server_property_args:
        server_property_args["onli"] = DEFAULT_ONLINE_MODE

    return server_property_args

def save_properties(server_path: str, server_property_args: dict[str, Any]) -> None:
    """Save all values from server_property_args to server.properties"""

    _validate_property_args(server_property_args)

    props_path = os.path.join(server_path, "server.properties")
    if not os.path.isfile(props_path):
        raise FileNotFoundError("File server.properties does not exist")

    with open(props_path, "r", encoding="utf8") as properties:
        lines = properties.readlines()

    for index, line in enumerate(lines):
        if "server-port=" in line:
            lines[index] = f"server-port={server_property_args['port']}\n"
        if "max-players=" in line:
            lines[index] = f"max-players={server_property_args['maxp']}\n"
        if "online-mode=" in line:
            lines[index] = f"online-mode={server_property_args['onli']}\n"

    if "server-port=" not in lines:
        lines.append(f"server-port={server_property_args['port']}\n")
    if "max-players=" not in lines:
        lines.append(f"max-players={server_property_args['maxp']}\n")
    if "online-mode=" not in lines:
        lines.append(f"online-mode={server_property_args['onli']}\n")

    with open(props_path, "w", encoding="utf8") as properties:
        properties.writelines(lines)

def _validate_property_args(server_property_args: dict[str, Any]):
    if server_property_args is None or not isinstance(server_property_args, dict):
        raise TypeError(f"Invalid type {type(server_property_args)} for server_property_args")
    if len(server_property_args) != PROPERTY_ARGS_COUNT:
        raise ValueError(f"Incorrect length of elements '{len(server_property_args)}'" + \
                         f" for server_property_args, expected '{PROPERTY_ARGS_COUNT}'")

    required_keys = ["port", "maxp", "onli"]
    for k in required_keys:
        if not k in server_property_args:
            raise KeyError(f"Missing key '{k}' in server_property_property_args")
    for item in server_property_args:
        if item not in required_keys:
            raise KeyError(f"Unexpected key '{k}' in server_property_property_args")
