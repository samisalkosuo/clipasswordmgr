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
#add command
#
from prompt_toolkit import prompt

from ..utils.utils import *
from ..utils.functions import *
from ..database.database import *
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class AddAccountCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        
        cmd_parser = ThrowingArgumentParser(prog="add",description='Add new account.')
        cmd_parser.add_argument('name',metavar='NAME', type=str, nargs=1, help='Account name.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):
        encryptionKey=GlobalVariables.KEY
        
        loadAccounts(encryptionKey,"add")
        name=self.cmd_args.name[0]

        if name is not None:
            print("Name     : %s" % name)
        else:
            name=prompt ("Name     : ")
            while name == "":
                print("Empty name not accepted")
                name=prompt ("Name     : ")
        URL=prompt ("URL      : ")
        username=askAccountUsername("User name")
        email=prompt("Email    : ")
        pwd=askAccountPassword("Password ","Password generator is available. Type your password or type 'p' to generate password.")
        comment=prompt ("Comment  : ")

        timestamp=formatTimestamp(currentTimestamp())

        newAccount=dict()
        newAccount[COLUMN_NAME]=name
        newAccount[COLUMN_URL]=URL
        newAccount[COLUMN_USERNAME]=username
        newAccount[COLUMN_EMAIL]=email
        newAccount[COLUMN_PASSWORD]=pwd
        newAccount[COLUMN_COMMENT]=comment
        newAccount[COLUMN_CREATED]=timestamp
        newAccount[COLUMN_UPDATED]=timestamp
        newAccount[COLUMN_ID]=generateNewID()
        accountString=makeAccountString(newAccount)
        debug(accountString)

        createPasswordFileBackups()
        insertAccountToFile(encryptionKey,accountString)

        print("Account added.")
