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
#template for commands - copy this to new file and rename and change this description
#

from ..utils.utils import *
from ..utils.functions import *
from ..database.database import *
from ..utils.settings import Settings
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class InfoCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        
        cmd_parser = ThrowingArgumentParser(prog="info",description='Information about the program.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        size=os.path.getsize(GlobalVariables.CLI_PASSWORD_FILE)
        formatString=getColumnFormatString(2,25,delimiter=": ",align="<")
        print(formatString.format("Version",GlobalVariables.VERSION))
        print(formatString.format("CLIPWDMGR_DATA_DIR",GlobalVariables.CLIPWDMGR_DATA_DIR))
        print(formatString.format("CLI_PASSWORD_FILE",GlobalVariables.CLI_PASSWORD_FILE))
        print(formatString.format("Password file size",sizeof_fmt(size)))

        loadAccounts(GlobalVariables.KEY)
        totalAccounts=selectFirst("select count(*) from accounts")
        print(formatString.format("Total accounts",str(totalAccounts)))
        lastUpdated=selectFirst("select updated from accounts order by updated desc")
        print(formatString.format("Last updated",lastUpdated))

        print(formatString.format("Settings file",Settings().getSettingsFile()))
        print("Settings:")
        printDictionary(SETTING_DEFAULT_VALUES,indent="  ")

