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
#delete command
#

from ..utils.utils import *
from ..database.database import *
from ..utils.functions import *
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class DeleteCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="delete",description='Delete account(s) that match given string.')
        cmd_parser.add_argument('name', metavar='NAME', type=str, nargs=1,help='Start of name.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        loadAccounts(GlobalVariables.KEY)
        arg=self.cmd_args.name[0]

        rows=list(executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg))
        if not rows:
            print("No accounts to delete.")
        for row in rows:
            printAccountRow(row)
            if boolValue(prompt("Delete this account (yes/no)? ")):
                sql="delete from accounts where %s=?" % (COLUMN_CREATED)
                executeDelete(sql,(row[COLUMN_CREATED],))
                saveAccounts()
                print("Account deleted.")

