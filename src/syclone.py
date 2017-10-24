import subprocess
from inspect import signature
import os
import lexer
import syc_parser
import time
import errormodule as er
import ASTtools

#the main application
class Console:
    #sets up the default commands dictionary
    def __init__(self):
        self.commands = {
            "i": self.In,
            "o": self.Out,
            "r": self.Run,
            "install": self.Install,
            "u": self.Update,
            "v": self.GetVersion(),
            "bug": self.Debug()
        }

        self.currentFile = ""
        self.fileType = ""

    def Debug(self):
        pass

    def GetVersion(self):
        pass

    def Install(self):
        pass

    def Update(self):
        pass

    def Out(self):
        pass

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
            self.Compile(" " + self.currentFile)
        else:
            raise NotImplementedError

    #gets input from user
    def GetInput(self):
        command = ""
        while(command != "exit"):
            #try:
                print(bcolors.MAGENTA + "SYC_VCP@x64 " + bcolors.GREEN + os.getcwd() + bcolors.YELLOW + " ~\n" + bcolors.WHITE + "$ ", end="")
                command = input("")
                # if is a syc command, the syc parser will handle it
                if (command.startswith("syc ")):
                    self.EvaluateCommand(command)
                #test if command is cd and revise current dir to compensate
                elif(command[:2] == "cd"):
                    os.chdir(command[3:])
                #else it will echo to console and print response
                elif (command != "exit"):
                    output = subprocess.check_output(command, shell=True)
                    print(str(output).replace("b'", "").replace("\\n", "\n").replace("\\r", "\r")[:len(output) - 1])
            #except Exception as e:
                #print(bcolors.RED + str(e))
                print("\n")

    #splits the command into its parts and executes it
    def EvaluateCommand(self, command):
        #removes unnecessary content
        command = command.strip("syc ")
        items = command.split(" ")
        args = []
        #divides into args and cmds
        for item in items:
            if(item in self.commands.keys()):
                args.append(("cmd", item))
            else:
                args.append(("arg", item))
        #sets up variable to see if cmd requires parameters
        reqParams = False
        #current function
        currentFunc = ""
        for item in args:
            #if it is a cmd it collects data about the cmd and sets current data for said cmd
            if(item[0] == "cmd"):
                #raises exception if there are not adequate params
                if(reqParams):
                    raise(CustomException("Commands arguments required."))
                #detects data about functions
                else:
                    #decides if cmd reqs params and if it exists at all
                    if (len(signature(self.commands[item[1]]).parameters) > 0):
                        reqParams = True
                        currentFunc = item[1]
                    else:
                        self.commands[item[1]]()
                        reqParams = False
            else:
                #handles passing in params
                if(not reqParams):
                    raise(CustomException("No arguments necessary."))
                else:
                    self.commands[currentFunc](item[1])
                    reqParams = False

    #main compile function
    def Compile(self, code):
        print(bcolors.BOLD + "Starting Compiler..." + bcolors.WHITE)
        print("\n", end="")
        #run preprocessor
        print("Running Preprocessor...\n")
        p_code = code
        self.Analyze(p_code)

    #gets semantically valid AST and catches compile time errors
    def Analyze(self, code):
        #sets error module code
        er.code = code
        #runs lexer
        print(bcolors.BLUE + "Lexing..." + bcolors.WHITE)
        lx = lexer.Lexer()
        tokens = lx.Lex(code)
        print((bcolors.YELLOW + "Found {0} tokens." + bcolors.WHITE).format(len(tokens)))
        print("\n", end="")
        #runs ll(1) parser
        print(bcolors.BLUE + "Parsing..." + bcolors.WHITE)
        pr = syc_parser.Parser()
        tree = pr.Parse(tokens)
        print(bcolors.YELLOW + "Generated AST." + bcolors.WHITE)
        print(tree)
        #cleans tree
        tree.content = ASTtools.ResolveAST(tree.content)
        # semantic analysis
        time.sleep(0.5)

class CustomException(Exception):
    pass

class bcolors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

cn = Console()
cn.GetInput()