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
#search-command
#

from ..database.database import *
from ..utils.utils import *
from ..utils.functions import *
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class SearchCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="search",description='Search accounts that match given string.')
        group = cmd_parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-u','--username',metavar='UNAME', type=str, help='Search by username.')
        group.add_argument('-e','--email',metavar='EMAIL', type=str, help='Search by email.')
        group.add_argument('searchstring', metavar='STRING', type=str, nargs='?',
                    help='Search string in name, url or comment.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        loadAccounts(GlobalVariables.KEY)
        where=""

        arg=self.cmd_args.username
        if arg is not None:
            where="where %s like '%%%s%%' " % (COLUMN_USERNAME,arg)

        arg=self.cmd_args.email
        if arg is not None:
            where="where %s like '%%%s%%' " % (COLUMN_EMAIL,arg)

        arg=self.cmd_args.searchstring
        if arg is not None:
            where="where %s like '%%%s%%' or %s like '%%%s%%' or %s like '%%%s%%' " % (COLUMN_NAME,arg,COLUMN_COMMENT,arg,COLUMN_URL,arg)


        rows=executeSelect([COLUMN_URL,COLUMN_ID,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],whereClause=where)
        printAccountRows(rows)

