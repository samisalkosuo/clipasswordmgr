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
#select-command
#
import sqlite3

from ..utils.utils import *
from ..utils.functions import *
from ..database.database import *
from ..utils.settings import Settings
from .SuperCommand import *
from ..globals import *
from ..globals import GlobalVariables

class SelectCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="select",description='Execute SELECT SQL statement and print results.')
        cmd_parser.add_argument('-i','--info', required=False, action='store_true',help="Accounts-table info.")
        cmd_parser.add_argument('statement', metavar='query_part', type=str, nargs='*',
                    help='Select SQL query parts.')

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        queryParts=self.cmd_args.statement
        if self.cmd_args.info==True or len(queryParts)==0:
            formatString=getColumnFormatString(2,20,delimiter=": ",align="<")
            print(formatString.format("Table","ACCOUNTS"))
            print(formatString.format("Columns",",".join(DATABASE_ACCOUNTS_TABLE_COLUMNS)))
            print()
            print("Example select-command:")
            print('  select * from accounts where email like \\"%acme.com\\"')
            return
        loadAccounts(GlobalVariables.KEY)
        sql="select %s" % (" ".join(queryParts))
        print("SQL: %s" % sql)
        try:
            (rows,columns)=executeSql(sql)
        except sqlite3.OperationalError as e:
            print("sqlite3.OperationalError: %s" % str(e))
            print('Escape quotes around strings: \\"%some string%\\"')
            return
        columnNames=[]
        for c in columns:
            columnNames.append(c[0])
        formatString=getColumnFormatString(len(columnNames),Settings().get(SETTING_DEFAULT_COLUMN_WIDTH))
        headerLine=formatString.format(*columnNames)
        print(headerLine)
        
        for row in rows:
            values=[]
            for cname in columnNames:
                value=row[cname]
                if cname==COLUMN_PASSWORD and Settings().getBoolean(SETTING_MASK_PASSWORD)==True:
                    value="********"
                values.append(shortenString(value))
            accountLine=formatString.format(*values)
            print(accountLine)

