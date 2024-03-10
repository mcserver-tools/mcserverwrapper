"""A simple global state logger"""

import os

logfile_path = ""

def setup(server_path, logfile_name):
    """Setup the logger"""

    global logfile_path
    logfile_path = os.path.join(server_path, logfile_name)

def delete_logs():
    """Delete the logfile"""

    if os.path.isfile(logfile_path):
        os.remove(logfile_path)

def log(msg: str, print_output = True):
    """
    Send a log message
    @param print_output: if set, print the msg to the console (default True)
    """

    with open(logfile_path, "a", encoding="utf8") as logfile:
        logfile.write(str(msg) + "\n")
    if print_output:
        print(str(msg))
