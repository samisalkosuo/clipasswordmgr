# -*- coding: utf-8 -*-

#The MIT License (MIT)
#
#Copyright (c) 2015,2018 Sami Salkosuo
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
#help-command


from ..utils.utils import *
from .SuperCommand import *
from ..globals import *


class HelpCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="help",description='This help.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):
        #implement this in subclass
        #check these always
        if self.help_text is not None:
            #return if help text for help-command was given
            return self.help_text
        if self.cmd_args is None:
            #return if no args or if -h or --help was given
            return

        #implement command here
        versionInfo()

        print()
        print("Commands:")

        maxLenName=0
        maxLenArgs=0
        maxLenDesc=0
        commandList=[]
        for cmdName in self.cmd_handler.cmdNameList:
            cmdObj=self.cmd_handler.commands[cmdName]
            cmdObj.parseCommandArgs([cmdName,"-HELP"])
            (args,desc)=cmdObj.executeCommand()
            args=args.replace(cmdName,"").strip()
            if len(cmdName)>maxLenName:
                maxLenName=len(cmdName)
            if len(args)>maxLenArgs:
                maxLenArgs=len(args)
            if len(desc)>maxLenDesc:
                maxLenDesc=len(desc)
            commandHelp=[cmdName,args,desc]
            commandList.append(commandHelp)

        formatStringName=getColumnFormatString(1,maxLenName,delimiter=" ",align="<")
        formatStringArgs=getColumnFormatString(1,maxLenArgs,delimiter=" ",align="<")
        formatStringDesc=getColumnFormatString(1,maxLenDesc,delimiter=" ",align="<")

        for c in commandList:
            print("  ",formatStringName.format(c[0]),formatStringArgs.format(c[1]),formatStringDesc.format(c[2]))

        print()
        print("Keyboard shortcuts:")
        print("  Keyboard shortcuts are available for the last account viewed using view-command.")
        print()
        print("  Ctrl-c Ctrl-c: Copy comment to clipboard.")
        print("  Ctrl-c Ctrl-e: Copy email to clipboard.")
        print("  Ctrl-c Ctrl-n: Copy user name to clipboard.")
        print("  Ctrl-c Ctrl-o: Open account URL in default browser.")
        print("  Ctrl-c Ctrl-p: Copy password to clipboard.")
        print("  Ctrl-c Ctrl-u: Copy URL to clipboard.")
            