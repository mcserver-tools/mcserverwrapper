import os
import pathlib

import requests
from mcserverwrapper import Wrapper

def download_server_jar():
    url = "https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar"
    server_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")

    req = requests.get(url)
    with open(os.path.join(server_path, "server.jar"), 'wb') as file:
        file.write(req.content)

if __name__ == "__main__":
    server_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
    os.makedirs(server_path, exist_ok=True)

    download_server_jar()

    wrapper = Wrapper(server_path=server_path)
    wrapper.startup()
    wrapper.send_command("/say hello minecraft")
    wrapper.stop()