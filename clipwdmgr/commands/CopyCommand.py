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
#copy-command
#

from ..utils.utils import *
from ..utils.functions import *
from ..database.database import *
from ..utils.settings import Settings
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class CopyCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="copy",description='Copy value of given field of account to clipboard.')
        group = cmd_parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-u','--username',action='store_true', help='Copy username to clipboard.')
        group.add_argument('-e','--email',action='store_true', help='Copy email to clipboard.')
        group.add_argument('-p','--password',action='store_true', help='Copy password to clipboard.')
        group.add_argument('-U','--url',action='store_true', help='Copy URL to clipboard.')
        group.add_argument('-c','--comment',action='store_true', help='Copy comment to clipboard.')

        cmd_parser.add_argument('account', metavar='NAME', type=str, nargs=1,
                    help='Account name.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        fieldToCopy=""
        fieldName=""
        if self.cmd_args.username==True:
            fieldToCopy=COLUMN_USERNAME
            fieldName="user name"
        if self.cmd_args.email==True:
            fieldToCopy=COLUMN_EMAIL
            fieldName="email"
        if self.cmd_args.password==True:
            fieldToCopy=COLUMN_PASSWORD
            fieldName="password"
        if self.cmd_args.url==True:
            fieldToCopy=COLUMN_URL
            fieldName="URL"
        if self.cmd_args.comment==True:
            fieldToCopy=COLUMN_COMMENT
            fieldName="comment"

        loadAccounts(GlobalVariables.KEY)
        arg=self.cmd_args.account[0]

        rows=executeSelect([COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],arg)
        for row in rows:
            #printAccountRow(row)
            name=row[COLUMN_NAME]
            f=row[fieldToCopy]
            if f=="":
                print("%s: %s is empty." % (name,fieldName))
            else:
                copyToClipboard(f,infoMessage="%s: %s copied to clipboard." % (name,fieldName),account=name,clipboardContent=fieldName)

