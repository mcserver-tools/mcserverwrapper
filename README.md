# McServerWrapper

A python package which wraps around a minecraft server, providing easy access for other programs which want to programmatically manage minecraft servers.

## Overview

### Supported Minecraft versions

#### Vanilla

Supports versions 1.7.10 to 1.20.4 (excluding 1.8.0, which is severely bugged, 1.8.1+ is fine again)

#### Forge

Supports versions 1.7.10 to 1.16.5 as well as 1.20.3 to 1.20.4

### Supported Python versions

Tested to work with Python versions 3.8 to 3.13.

### Supported operating systems

Tested to work on Windows 10 and Ubuntu.

Different Linux distros and Windows 11 might work as well. If not, please open a new issue.

## Installation

### PyPi

Not yet available

### Github

To install the latest version directly from Github, run the following command:
```bash
pip install git+https://github.com/mcserver-tools/mcserverwrapper.git
```

This will automatically install all other dependencies.

## Usage

A simple usage example is shown below:
```python
from mcserverwrapper import Wrapper

wrapper = Wrapper("/my/server/directory/server.jar")
wrapper.startup()
wrapper.send_command("/say hello minecraft")
wrapper.stop()
```

In this example, a minecraft server is started by providing the path to its server.jar file.
After startup, it sends a command to the server.
Finally, the server is stopped gracefully.

More examples can be found in the **examples** folder.

## Development environment setup

If you want to contribute to this project, you need to set up your local environment.

### Clone the repository

Run the command
```bash
git clone https://github.com/mcserver-tools/mcserverwrapper
cd mcserverwrapper
```
in your terminal.

### Install pip packages

To install all optional as well as development python packages, run the following commands in the project root.

Windows:
```bash
py -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node

Node 20 is needed to use MineFlayer.
The install instructions can be found below:

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

### Add credentials for testing

To simulate a player connecting to the server, it needs to authenticate against microsofts servers. This means, that a microsoft account which owns Minecraft is needed. Don't worry, the credentials are only saved locally.

Create a new file named *password.txt* in the repository root and add the following content (without the brackets):
```
(username-here)
(password-here)
```

### Run tests

After installing all of the requirements, the tests can be ran using
```bash
python -m pytest src -rs --skip-linting --skip-test-all
```

If you want to run tests for all Minecraft versions, remove the `--skip-test-all` argument from the command above.

> **Warning**
> Beware that testing all versions can take multiple hours!

### Git pre-commit hooks

Pre-commit hooks are used to check and autofix formatting issues and typos before you commit your changes.
Once installed, they run automatically if you run `git commit ...`.

Using these is optional, but encouraged.

```bash
pip install pre-commit
pre-commit install
```

To verify the installation and run all checks:
```bash
pre-commit run --all-files
```
