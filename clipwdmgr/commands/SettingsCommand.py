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
#settings-command
#

from ..utils.utils import *
from ..utils.functions import *
from ..utils.settings import Settings
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class SettingsCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    def parseCommandArgs(self,userInputList):
        #implement in command class
        #parse arguments like in this method
        cmd_parser = ThrowingArgumentParser(prog="settings",description='Program settings.')
        cmd_parser.add_argument('-s','--set', metavar='KEY=VALUE',help='Set or edit setting.')
        cmd_parser.add_argument('--reset', required=False, action='store_true', help='Reset settings to defaults.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):
        #settings may include: complete word whe ntyping, completion type readline
        #toolbar, column length, default uname format etc etc

        settingsObj=Settings()

        if self.cmd_args.reset:
            settingsObj.resetSettings()
            print("Settings reset.")
            return

        if self.cmd_args.set is not None:
            #add new setting
            newSetting=self.cmd_args.set.split("=")
            settingsObj.set(newSetting[0],newSetting[1])
            print("Setting saved: %s=%s" %(newSetting[0],newSetting[1]))
            return
        
        #no args, print settings
        printDictionary(SETTING_DEFAULT_VALUES)

