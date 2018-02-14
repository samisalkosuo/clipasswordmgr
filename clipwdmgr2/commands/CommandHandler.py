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
#Handle/execute user commands
import shutil
import shlex
from .UserNameCommand import *
from .PasswordCommand import *
from .HelpCommand import *

from ..globals import *
from ..crypto.crypto import *
from ..utils.utils import *


#CommandHandler class to handle user input commands
class CommandHandler:
    
    def __init__(self):
        self.commands={}
        self.commands["uname"]=UserNameCommand(self)
        self.commands["pwd"]=PasswordCommand(self)
        self.commands["help"]=HelpCommand(self)


    def execute(self,userInput):

        #get list of userInput
        userInputList=shlex.split(userInput)
        if len(userInputList)==0:
            #should not happen
            print("No input!!")
            return
        #cmdName is the first in input list
        cmdName=userInputList[0]
        returnValue=None
        try:
            commandObject=self.commands[cmdName]
        except KeyError:
            print("%s is unrecognized."% cmdName)
        else:
            #execute
            commandObject.parseCommandArgs(userInputList)
            returnValue=commandObject.executeCommand()
        
        return returnValue
