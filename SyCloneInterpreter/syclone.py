import analyzers
import subprocess
from inspect import signature
import re

#the main application
class Console:
    #sets up the default commands dictionary
    def __init__(self):
        self.commands = {
            "-i": self.In,
            "-o": self.Out,
            "-log": self.Log,
            "-r": self.Run,
            "-get": self.Install,
            "-u": self.Update
        }
        self.currentFile = ""
        self.fileType = ""

    def Install(self):
        pass

    def Update(self):
        pass

    def Out(self):
        pass

    def Log(self, level):
        global loglevel
        if(level == "debug"):
            loglevel = 0
        elif(level == "status"):
            loglevel = 1
        elif(level == "warn"):
            loglevel = 2
        elif(level == "fatal"):
            loglevel = 3
        else:
            raise CustomException("Invalid Log Level.")

    #brings in a file
    def In(self, path):
        if(path.endswith(".sy") or path.endswith(".txt")):
            self.fileType = "source"
        elif(path.endswith(".sbc")):
            self.fileType = "bytecode"
        elif(path.endswith(".syo")):
            self.fileType = "object"
        else:
            raise CustomException("Invalid file type.")
        with open(path) as fileObject:
            for item in fileObject:
                self.currentFile += item

    #runs a file
    def Run(self):
        if(self.fileType == "source"):
            analyzers.Compile(" " + self.currentFile)
            analyzers.Compile(" " + self.currentFile)
        else:
            raise NotImplementedError

    #gets input from user
    def GetInput(self):
        command = ""
        while(command != "exit"):
            try:
                command = input("")
                # if is a syc command, the syc parser will handle it
                if (command.startswith("syc ")):
                    self.EvaluateCommand(command)
                # else it will echo it to the command prompt and print the response
                elif (command != "exit"):
                    output = subprocess.check_output(command, shell=True)
                    print(str(output).replace("b'", "").replace("\\n", "\n").replace("\\r", "\r")[:len(output) - 1])
            except Exception as e:
                print(e)

    #splits the command into its parts and executes it
    def EvaluateCommand(self, command):
        i = 0
        #catches all arguments
        args = re.findall(r'"([^"]*)"', command)
        for item in args:
            command = command.replace("\"" + item + "\"", "")
        #trims lux of off command before splitting begins
        command = command[4:]
        #splits and stores all desired commands
        cmds = command.split(" ")
        #executes command in order
        for cmd in cmds:
            if(cmd in self.commands.keys()):
                # determines if command takes arguments or not
                if (len(signature(self.commands[cmd]).parameters) > 0):
                    self.commands[cmd](args[i])
                else:
                    self.commands[cmd]()
                i += 1
            else:
                if(cmd != ""):
                    raise CustomException("Invalid Command.")
                else:
                    pass

class CustomException(Exception):
    pass


cn = Console()
cn.GetInput()