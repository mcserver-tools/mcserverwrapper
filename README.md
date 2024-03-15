# McServerWrapper

A python package which wraps around a minecraft server, providing easy access for python programs which want to automatically manage minecraft servers.

## Overview

Examples can be found in the **examples** folder.

Supported Minecraft versions:

### Vanilla

Supports versions 1.7.10 to 1.20.4 (excluding 1.8.0, which is severely bugged).

### Forge

Supports version 1.7.10 to 1.16.5 as well as 1.20.3 to 1.20.4

## Installation

### PyPi

Not yet available

### Github

To install the latest version directly from Github, run the following command:
```pip install git+https://github.com/mcserver-tools/mcserverwrapper.git```

This will automatically install all other dependencies.

## Run tests locally

In order to run tests locally, there are a few things that have to be setup:

### Add credentials for testing

To simulate a player connecting ot the server, it needs to authenticate against microsofts servers. This means, that a microsoft account which owns Minecraft is needed. Don't worry, the credentials are only saved locally.

Create a new file named *password.txt* in the repository root and add the following content (without the brackets):
```
(username-here)
(password-here)
```

### Node

Node 20 is needed to use MineFlayer.

#### Windows

It can be downloaded from [here](https://nodejs.org/en/download).

#### Debian/Ubuntu

Install it using the commands found (here)[https://github.com/nodesource/distributions?tab=readme-ov-file#debian-and-ubuntu-based-distributions].

### MineFlayer

To simulate a player connecting to the test server, [MineFlayer](https://github.com/PrismarineJS/mineflayer) is used.

It can be installed by running
```bash
npm install mineflayer
```

### Java

To actually run a minecraft server, a Java 21 JRE needs to be installed and added to the path.

Download it from (here)[https://adoptium.net/temurin/releases/].

### Run tests

After installing all of the requirements, the tests can be ran using
```bash
python -m pytest
```
