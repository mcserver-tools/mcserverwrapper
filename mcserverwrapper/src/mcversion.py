"""Module containing everything regarding to minecraft versions"""

import re

class McVersionType:
    """Enum containing the different Minecraft version types"""

    UNKNOWN = 0
    VANILLA = 1
    SNAPSHOT = 2
    FORGE = 3
    PAPER = 4
    SPIGOT = 5
    BUKKIT = 6

    @staticmethod
    def get_all() -> dict[str, int]:
        """Return all different version types"""

        return {
            "UNKNOWN": 0,
            "VANILLA": 1,
            "SNAPSHOT": 2,
            "FORGE": 3,
            "PAPER": 4,
            "SPIGOT": 5,
            "BUKKIT": 6
        }

    @staticmethod
    def get_name(type_in: int) -> str:
        """Get the name of a given mc version type"""

        for name, type_id in McVersionType.get_all().items():
            if type_id == type_in:
                return name

        raise ValueError(f"Version type with id {type_in} not found")

class McVersion:
    """Class representing the version and version type of a minecraft server"""

    def __init__(self, name: str, version_type: int) -> None:
        if not isinstance(name, str):
            raise TypeError(f"Expected str, got {type(name)}")
        if not isinstance(version_type, int):
            raise TypeError(f"Expected int, got {type(version_type)}")

        if re.search(r"^1\.[1-2]{0,1}[0-9](\.[0-9]{1,2})?$", name) is None:
            raise ValueError(f"Expected version regex to match with {name}")

        self.name = name
        self.type = version_type

        split_name = [int(item) for item in name.split(".")]
        if len(split_name) == 2:
            self.id = split_name[0] * 10**4 + split_name[1] * 10**2
        elif len(split_name) == 3:
            self.id = split_name[0] * 10**4 + split_name[1] * 10**2 + split_name[2]
        else:
            raise ValueError(f"Expected to version to have at most 3 subparts, but received {split_name}")

    name: str
    type: int
    id: int

    def __str__(self) -> str:
        if self.type == McVersionType.VANILLA:
            return f"{self.name}"

        return f"{McVersionType.get_name(self.type)} {self.name}"
