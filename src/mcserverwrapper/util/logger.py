"""A simple global state logger"""

import os

LOGFILE_NAME = "mcserverwrapper.log"

# pylint: disable-next=invalid-name
logfile_path = None

def setup(server_path):
    """Setup the logger"""

    if not os.path.isdir(server_path):
        raise Exception(f"Directory {server_path} not found")

    global logfile_path
    logfile_path = os.path.join(server_path, LOGFILE_NAME)

    if not os.path.isfile(logfile_path):
        with open(logfile_path, "w+", encoding="utf8"):
            pass

def delete_logs():
    """Delete the logfile"""

    if os.path.isfile(logfile_path):
        os.remove(logfile_path)

def log(msg: str, print_output = True):
    """
    Send a log message
    @param print_output: if set, print the msg to the console (default True)
    """

    if logfile_path is None:
        raise Exception("Logger not yet set up")

    with open(logfile_path, "a", encoding="utf8") as logfile:
        logfile.write(str(msg) + "\n")
    if print_output:
        print(str(msg))
