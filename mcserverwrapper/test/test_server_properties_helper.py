"""Test the server_properties_helper methods"""

import pathlib
import os

from mcserverwrapper.src.mcversion import McVersion, McVersionType
from ..src import server_properties_helper as sph

def test_get_mixed_params():
    """Tests the helper with mixed params"""

    props = {
        "server-port": 25506,
        "max-players": 18,
        "some-unknown-prop": "hehe",
        "online-mode": "true",
        "level-type": "minecraft\\:normal",
        "use-native-transport": "false"
    }

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+", encoding="utf8") as props_file:
        props_file.write("\n".join([f"{key}={value}" for key, value in props.items()]))

    result = sph.get_properties(props_path, McVersion("1.20", McVersionType.VANILLA))

    assert len(result) == 5
    assert result["maxp"] == props["max-players"]
    assert result["onli"] == props["online-mode"]
    assert result["port"] == props["server-port"]
    assert result["levt"] == props["level-type"]
    assert result["untp"] == props["use-native-transport"]

def test_parse_custom_params():
    """Tests the helper with custom params"""

    props = {
        "port": 25590,
        "maxp": 21,
        "onli": "false",
        "levt": "minecraft\\:normal",
        "untp": "false"
    }

    result = sph.parse_properties_args(os.getcwd(), props, McVersion("1.20", McVersionType.VANILLA))

    # ensure that props didn't change
    assert len(props) == 5
    assert props["port"] == 25590
    assert props["maxp"] == 21
    assert props["onli"] == "false"
    assert props["levt"] == "minecraft\\:normal"
    assert props["untp"] == "false"

    assert len(result) == 5
    assert result["port"] == 25590
    assert result["maxp"] == 21
    assert result["onli"] == "false"
    assert result["levt"] == "minecraft\\:normal"
    assert result["untp"] == "false"

def test_parse_default_params():
    """Tests the helper without custom params"""

    props = { }

    result = sph.parse_properties_args(os.getcwd(), props, McVersion("1.20", McVersionType.VANILLA))

    # ensure that props didn't change
    assert len(props) == 0
    assert "port" not in props
    assert "maxp" not in props
    assert "onli" not in props
    assert "levt" not in props
    assert "untp" not in props

    assert len(result) == 5
    assert result["port"] == sph.DEFAULT_PORT
    assert result["maxp"] == sph.DEFAULT_MAX_PLAYERS
    assert result["onli"] == sph.DEFAULT_ONLINE_MODE
    assert result["levt"] == sph.DEFAULT_LEVEL_TYPE_POST_1_19
    assert result["untp"] == sph.DEFAULT_USE_NATIVE_TRANSPORT

def test_params_with_file():
    """Tests the helper with a server.properties file"""

    props_test_data = "server-port=25599\n" + \
                      "some-other-prop=haha\n" + \
                      "max-players=30\n" + \
                      "a-final-prop=aha\n" + \
                      "online-mode=true\n"

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+", encoding="utf8") as props_file:
        props_file.write(props_test_data)

    props = {
        "maxp": 22,
        "untp": "true"
    }

    result = sph.parse_properties_args(props_path, props, McVersion("1.20", McVersionType.VANILLA))

    # ensure that props didn't change
    assert len(props) == 2
    assert "port" not in props
    assert props["maxp"] == 22
    assert "onli" not in props
    assert "levt" not in props
    assert props["untp"] == "true"

    assert len(result) == 5
    assert result["port"] == 25599
    assert result["maxp"] == 22
    assert result["onli"] == "true"
    assert result["levt"] == "minecraft\\:normal"
    assert result["untp"] == "true"

def test_parse_mixed_params_1():
    """Tests the helper with custom and default params"""

    props = {
        "port": 25541,
        "untp": "false"
    }

    result = sph.parse_properties_args(os.getcwd(), props, McVersion("1.20", McVersionType.VANILLA))

    # ensure that props didn't change
    assert len(props) == 2
    assert props["port"] == 25541
    assert "maxp" not in props
    assert "onli" not in props
    assert "levt" not in props
    assert props["untp"] == "false"

    assert len(result) == 5
    assert result["port"] == 25541
    assert result["maxp"] == sph.DEFAULT_MAX_PLAYERS
    assert result["onli"] == sph.DEFAULT_ONLINE_MODE
    assert result["levt"] == sph.DEFAULT_LEVEL_TYPE_POST_1_19
    assert result["untp"] == "false"

def test_parse_mixed_params_2():
    """Tests the helper with custom and default params"""

    props = {
        "maxp": 43,
        "onli": "false",
        "levt": "default"
    }

    result = sph.parse_properties_args(os.getcwd(), props, McVersion("1.20", McVersionType.VANILLA))

    # ensure that props didn't change
    assert len(props) == 3
    assert "port" not in props
    assert props["maxp"] == 43
    assert props["onli"] == "false"
    assert props["levt"] == "default"
    assert "untp" not in props

    assert len(result) == 5
    assert result["port"] == sph.DEFAULT_PORT
    assert result["maxp"] == 43
    assert result["onli"] == "false"
    assert result["levt"] == sph.DEFAULT_LEVEL_TYPE_POST_1_19
    assert result["untp"] == sph.DEFAULT_USE_NATIVE_TRANSPORT

def test_save_existing():
    """Tests the helper save function with valid params"""

    props_test_data = "server-port=25599\n" + \
                      "some-other-prop=haha\n" + \
                      "max-players=30\n" + \
                      "a-final-prop=aha\n" + \
                      "online-mode=false"

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+", encoding="utf8") as props_file:
        props_file.write(props_test_data)

    props = {
        "port": 25546,
        "maxp": 21,
        "onli": "true",
        "levt": sph.DEFAULT_LEVEL_TYPE_POST_1_19,
        "untp": "false"
    }

    sph.save_properties(props_path, props)

    # ensure that props didn't change
    assert len(props) == 5
    assert props["port"] == 25546
    assert props["maxp"] == 21
    assert props["onli"] == "true"
    assert props["levt"] == sph.DEFAULT_LEVEL_TYPE_POST_1_19
    assert props["untp"] == "false"

    with open(os.path.join(props_path, "server.properties"), "r", encoding="utf8") as props_file:
        lines = props_file.read().splitlines()

    assert len(lines) == 7
    assert lines[0] == "server-port=25546"
    assert lines[1] == "some-other-prop=haha"
    assert lines[2] == "max-players=21"
    assert lines[3] == "a-final-prop=aha"
    assert lines[4] == "online-mode=true"
    assert lines[5] == "level-type=minecraft\\:normal"
    assert lines[6] == "use-native-transport=false"

def test_save_new():
    """Tests the helper save function with valid params"""

    props_test_data = "some-other-prop=haha\n" + \
                      "a-final-prop=aha\n"

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+", encoding="utf8") as props_file:
        props_file.write(props_test_data)

    props = {
        "port": 25546,
        "maxp": 21,
        "onli": "true",
        "levt": "minecraft\\:normal",
        "untp": "true"
    }

    sph.save_properties(props_path, props)

    # ensure that props didn't change
    assert len(props) == 5
    assert props["port"] == 25546
    assert props["maxp"] == 21
    assert props["onli"] == "true"
    assert props["levt"] == "minecraft\\:normal"
    assert props["untp"] == "true"

    with open(os.path.join(props_path, "server.properties"), "r", encoding="utf8") as props_file:
        lines = props_file.read().splitlines()

    assert len(lines) == 7
    assert lines[0] == "some-other-prop=haha"
    assert lines[1] == "a-final-prop=aha"
    assert lines[2] == "server-port=25546"
    assert lines[3] == "max-players=21"
    assert lines[4] == "online-mode=true"
    assert lines[5] == "level-type=minecraft\\:normal"
    assert lines[6] == "use-native-transport=true"
