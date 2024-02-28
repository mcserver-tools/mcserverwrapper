import pathlib
import os

import pytest

from mcserverwrapper.src import server_properties_helper as sph

def test_parse_custom_params():
    """Tests the helper with custom params"""

    props = {
        "port": 25590,
        "maxp": 21,
        "onli": "false"
    }

    result = sph.parse_properties_args(os.getcwd(), props)

    # ensure that props didn't change
    assert props["port"] == 25590
    assert props["maxp"] == 21
    assert props["onli"] == "false"

    assert result["port"] == 25590
    assert result["maxp"] == 21
    assert result["onli"] == "false"

def test_parse_default_params():
    """Tests the helper without custom params"""

    props = { }

    result = sph.parse_properties_args(os.getcwd(), props)

    # ensure that props didn't change
    assert "port" not in props
    assert "maxp" not in props
    assert "onli" not in props

    assert result["port"] == sph.DEFAULT_PORT
    assert result["maxp"] == sph.DEFAULT_MAX_PLAYERS
    assert result["onli"] == sph.DEFAULT_ONLINE_MODE

def test_params_with_file():
    """Tests the helper with a server.properties file"""

    props_test_data = "server-port=25599\n" + \
                      "some-other-prop=haha\n" + \
                      "max-players=30\n" + \
                      "a-final-prop=aha\n" + \
                      "online-mode=true\n"

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+") as props_file:
        props_file.write(props_test_data)

    props = {
        "maxp": 22
    }

    result = sph.parse_properties_args(props_path, props)

    # ensure that props didn't change
    assert "port" not in props
    assert props["maxp"] == 22
    assert "onli" not in props

    assert result["port"] == 25599
    assert result["maxp"] == 22
    assert result["onli"] == "true"

def test_parse_mixed_params_1():
    """Tests the helper with custom and default params"""

    props = { 
        "port": 25541
    }

    result = sph.parse_properties_args(os.getcwd(), props)

    # ensure that props didn't change
    assert props["port"] == 25541
    assert "maxp" not in props
    assert "onli" not in props

    assert result["port"] == 25541
    assert result["maxp"] == sph.DEFAULT_MAX_PLAYERS
    assert result["onli"] == sph.DEFAULT_ONLINE_MODE

def test_parse_mixed_params_2():
    """Tests the helper with custom and default params"""

    props = { 
        "maxp": 43,
        "onli": "false"
    }

    result = sph.parse_properties_args(os.getcwd(), props)

    # ensure that props didn't change
    assert "port" not in props
    assert props["maxp"] == 43
    assert props["onli"] == "false"

    assert result["port"] == sph.DEFAULT_PORT
    assert result["maxp"] == 43
    assert result["onli"] == "false"

def test_save_existing():
    """Tests the helper save function with valid params"""

    props_test_data = "server-port=25599\n" + \
                      "some-other-prop=haha\n" + \
                      "max-players=30\n" + \
                      "a-final-prop=aha\n" + \
                      "online-mode=false"

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+") as props_file:
        props_file.write(props_test_data)

    props = {
        "port": 25546,
        "maxp": 21,
        "onli": "true"
    }

    sph.save_properties(props_path, props)

    # ensure that props didn't change
    assert props["port"] == 25546
    assert props["maxp"] == 21
    assert props["onli"] == "true"

    with open(os.path.join(props_path, "server.properties"), "r") as props_file:
        lines = props_file.read().splitlines()
    
    assert lines[0] == "server-port=25546"
    assert lines[1] == "some-other-prop=haha"
    assert lines[2] == "max-players=21"
    assert lines[3] == "a-final-prop=aha"
    assert lines[4] == "online-mode=true"

def test_save_new():
    """Tests the helper save function with valid params"""

    props_test_data = "some-other-prop=haha\n" + \
                      "a-final-prop=aha\n"

    props_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    with open(os.path.join(props_path, "server.properties"), "w+") as props_file:
        props_file.write(props_test_data)

    props = {
        "port": 25546,
        "maxp": 21,
        "onli": "true"
    }

    sph.save_properties(props_path, props)

    # ensure that props didn't change
    assert props["port"] == 25546
    assert props["maxp"] == 21
    assert props["onli"] == "true"

    with open(os.path.join(props_path, "server.properties"), "r") as props_file:
        lines = props_file.read().splitlines()
    
    assert lines[0] == "some-other-prop=haha"
    assert lines[1] == "a-final-prop=aha"
    assert lines[2] == "server-port=25546"
    assert lines[3] == "max-players=21"
    assert lines[4] == "online-mode=true"
