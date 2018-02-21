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
#super class of commands

class SuperCommand:

    def __init__(self,cmd_handler):
        self.cmd_args=None
        self.help_text=None
        self.cmd_handler=cmd_handler

    #parser command line args. args are like: cmd -arg1 -arg2 val1
    #implement this in subclass
    def parseCommandArgs(self,userInputList):
        pass

    def executeCommand(self):
        #this is executed by command handler and help-command
        #calls subclass execute() and returns help text if any
        #help text is used by help-command
        #do not override this in subclasses
        
        #check these always
        if self.help_text is not None:
            #return if help text for help-command was given
            return self.help_text
        if self.cmd_args is None:
            #return if no args or if -h or --help was given
            return None

        self.execute()
        
    #execute command
    #override and implement in subclass
    def execute(self):
        pass

    