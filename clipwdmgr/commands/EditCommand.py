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
#edit command
#

from ..utils.utils import *
from ..database.database import *
from ..utils.functions import *
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class EditCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="edit",description='Edit account(s) that match given string.')
        cmd_parser.add_argument('name', metavar='NAME', type=str, nargs=1,
                    help='Start of name.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        loadAccounts(GlobalVariables.KEY)
        arg=self.cmd_args.name[0]

        #put results in list so that update cursor doesn't interfere with select cursor when updating account
        #there note about this here: http://apidoc.apsw.googlecode.com/hg/cursor.html
        rows=list(executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg))
        for row in rows:
            printAccountRow(row)
            if boolValue(prompt("Edit this account (yes/no)? ")):
                values=[]
                name=modPrompt("Name",row[COLUMN_NAME])
                values.append(name)

                URL=modPrompt("URL",row[COLUMN_URL])
                values.append(URL)

                oldUserName=row[COLUMN_USERNAME]
                promptStr="User name OLD: (%s) NEW" % oldUserName
                username=askAccountUsername(promptStr,oldUserName)
                values.append(username)

                email=modPrompt("Email",row[COLUMN_EMAIL])
                values.append(email)

                originalPassword=row[COLUMN_PASSWORD]
                pwd=askAccountPassword("Password OLD: (%s) NEW:" % (originalPassword),"Password generator is available. Type your password or type 'p'/'ps' to generate password or 'c' to use original password.",originalPassword)

                values.append(pwd)

                comment=modPrompt("Comment",row[COLUMN_COMMENT])
                values.append(comment)

                updated=formatTimestamp(currentTimestamp())
                values.append(updated)

                created=row[COLUMN_CREATED]
                values.append(created)

                sql="update accounts set %s=?,%s=?,%s=?,%s=?,%s=?,%s=?,%s=? where %s=?" % (
                    COLUMN_NAME,
                    COLUMN_URL,
                    COLUMN_USERNAME,
                    COLUMN_EMAIL,
                    COLUMN_PASSWORD,
                    COLUMN_COMMENT,
                    COLUMN_UPDATED,
                    COLUMN_CREATED
                    )
                executeSql(sql,tuple(values),commit=True)
                saveAccounts()
                print("Account updated.")
