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
#encrypt command
#

from ..crypto.crypto import *
from ..utils.utils import *
from ..utils.functions import *
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class EncryptCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):

        cmd_parser = ThrowingArgumentParser(prog="encrypt",description='Encrypt selected accounts(s).')
        cmd_parser.add_argument('-p','--passphrase', metavar='STR',help='Encryption passphrase.')
        cmd_parser.add_argument('-n','--nocopy', required=False, action='store_true',help="Do not copy encrypted string to clipboard.")
        cmd_parser.add_argument('accounts', metavar='account_name', type=str, nargs='+',
                    help='Account names, or beginning of account names, to encrypt.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        for arg in self.cmd_args.accounts:
            loadAccounts(GlobalVariables.KEY)
            rows=executeSelect(DATABASE_ACCOUNTS_TABLE_COLUMNS,arg)
            key=GlobalVariables.KEY
            if self.cmd_args.passphrase != None:
                key=createKey(self.cmd_args.passphrase)
            
            for row in rows:
                name=row[COLUMN_NAME]
                encryptedString=encryptAccountRow(row,key)
                print("%s: %s" % (name,encryptedString))
                if self.cmd_args.nocopy==False:
                    copyToClipboard(encryptedString,infoMessage="Encrypted account copied to clipboard.",account=name,clipboardContent="encrypted text")

