# McServerWrapper

A wrapper for minecraft servers, usable as a python package or from the console.

## Overview

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
