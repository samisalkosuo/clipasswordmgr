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
#view-command

#views account info
#

from ..database.database import *
from ..utils.utils import *
from ..utils.functions import *
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables


class ViewAccountCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        
        cmd_parser = ThrowingArgumentParser(prog="view",description='View account(s) details that start with given string and have matching username and/or comment.')
        cmd_parser.add_argument('-u','--username',metavar='UNAME', required=False, type=str, help='Account includes username.')
        cmd_parser.add_argument('-c','--comment',metavar='COMMENT', required=False, type=str, help='String in comment field.')
        cmd_parser.add_argument('-e','--encrypt', required=False, action='store_true', help='View account as encrypted string.')

        cmd_parser.add_argument('account', metavar='NAME', type=str, nargs=1,
                    help='Account name.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        accountsLoaded=loadAccounts(GlobalVariables.KEY)
        if accountsLoaded == False:
            #no accounts, so return
            return

        arg=self.cmd_args.account[0]

        where="where name like \"%s%%\"" % arg

        arg=self.cmd_args.username
        if arg:
            where=where+" and username like '%%%s%%'" % (arg)

        arg=self.cmd_args.comment
        if arg:
            where=where+" and comment like '%%%s%%'" % (arg)

        rows=executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg,whereClause=where)
        for row in rows:
            if self.cmd_args.encrypt==True:
                encryptedAccount=encryptAccountRow(row)
                print(encryptedAccount)
                copyToClipboard(encryptedAccount,infoMessage="Encrypted account copied to clipboard.")
            else:
                printAccountRow(row)
                pwd=row[COLUMN_PASSWORD]
                if CONFIG[CFG_COPY_PASSWORD_ON_VIEW]==True:
                    print()
                    copyToClipboard(pwd,infoMessage="Password copied to clipboard.")

