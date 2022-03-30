import subprocess
from time import sleep
from pexpect import popen_spawn
import os
import os.path
import pexpect

class ServerWrapper():
    def __init__(self) -> None:
        os.chdir(os.getcwd() + "\TestServer")

        # delete old logfile
        if os.path.exists("logfile.txt"):
            os.system("del logfile.txt")

    def startup(self):
        # f = open("logfile.txt", "ab")
        self.child = popen_spawn.PopenSpawn("java -Xmx2G -jar server.jar nogui", timeout=1)

        # wait until the server finished starting
        while True:
            # print out the startup logs
            output = b""
            while True:
                try:
                    output += self.child.read(1)
                except pexpect.exceptions.TIMEOUT:
                    break
            output = output.decode("ascii").replace("\n", "")
            if output != "":
                print(output)
                with open("logfile.txt", "a") as logfile:
                    logfile.write(output)
                if "For help, type" in output:
                    break

    def send_command(self, command, wait_time):
        self.child.sendline(command)
        sleep(wait_time)

        output = b""
        try:
            while True:
                output += self.child.read(10)
        except pexpect.exceptions.TIMEOUT:
            try:
                while True:
                    read = self.child.read(1)
                    if read == "":
                        break
                    else:
                        output += read
            except pexpect.exceptions.TIMEOUT:
                pass

        print(command)
        print(output.decode("ascii"))
        with open("logfile.txt", "ab") as logfile:
            logfile.write((command + "\n").encode("ascii"))
            logfile.write(output)
        return output.decode("ascii")

    def stop(self):
        self.child.sendline("/stop")
        self.child.wait()
        output = self.child.read(-1)
        print(output.decode("ascii"))
        with open("logfile.txt", "ab") as logfile:
            logfile.write(("/stop\n").encode("ascii"))
            logfile.write(output)

wrapper = ServerWrapper()
wrapper.startup()
wrapper.send_command("/time set day", 1)
wrapper.send_command("/time set night", 1)
wrapper.stop()

exit()

p = subprocess.Popen("cmd /k java -Xmx2G -jar server.jar nogui", shell=True, stdin=subprocess.PIPE, stdout=f, stderr=f, text=True)

# change directory
# p.stdin.write("cd ./TestServer; echo Text")

# cmd = ["java", "-Xmx2G", "-jar", "server.jar", "nogui"]
# start the server
# p.stdin.write("java -Xmx2G -jar server.jar nogui")
# p.communicate()
# stdOutput, stdError = p.communicate()
# print(stdOutput)
