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

#various functions used by the program
import shutil

from prompt_toolkit import prompt

from ..globals import *
from ..globals import GlobalVariables
from ..utils.settings import Settings
from .utils import *
from ..database.database import *


def printAccountRow(row):
    formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
    print("===============================")# % (name))
    #fields=[COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_COMMENT]

    for field in row.keys():#fields:
        value=row[field]
        if field==COLUMN_PASSWORD and Settings().getBoolean(SETTING_MASK_PASSWORD_ON_VIEW)==True:
            value="********"
        print(formatString.format(field,value))


def printAccountRows(rows):
    #print account rows in columns
    #used by list and search commands
    
    columnLength=Settings().getInt(SETTING_DEFAULT_COLUMN_WIDTH)
    formatString=getColumnFormatString(6,columnLength)
    headerLine=formatString.format(COLUMN_NAME,COLUMN_ID,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT)
    print(headerLine)
    for row in rows:
        pwd=row[COLUMN_PASSWORD]
        if Settings().getBoolean(SETTING_MASK_PASSWORD)==True:
            pwd="********"
        pwd=shortenString(pwd)
        accountLine=formatString.format(shortenString(row[COLUMN_NAME]),shortenString(row[COLUMN_ID]),shortenString(row[COLUMN_URL]),shortenString(row[COLUMN_USERNAME]),shortenString(row[COLUMN_EMAIL]),pwd,shortenString(row[COLUMN_COMMENT]))
        print(accountLine)

def shortenString(string):
    string=str(string)
    columnWidth=Settings().getInt(SETTING_DEFAULT_COLUMN_WIDTH)
    if len(string)>columnWidth:
        string="%s..." % string[0:columnWidth-3]
    return string

def saveAccounts():
    #save accounts
    #selet all accounts from accounts db
    #encrypt one at a time and save to file

    createPasswordFileBackups()

    accounts=[]
    rows=executeSelect(DATABASE_ACCOUNTS_TABLE_COLUMNS,None,None)
    for row in rows:
        encryptedAccount=encryptAccountRow(row)
        accounts.append(encryptedAccount)

    createNewFile(GlobalVariables.CLI_PASSWORD_FILE,accounts)

def encryptAccountRow(row,key=None):
    #create string of account and encrypt
    account=[]
    for columnName in row.keys():
        value=row[columnName]
        if value != None:
            value=str(value)
            value=value.strip()
        account.append("%s:%s" % (columnName,value))
    if key==None:
        key=GlobalVariables.KEY
    return encryptString(key,FIELD_DELIM.join(account))

def makeAccountString(accountDict):
    account=[]
    for key in accountDict:
        value=accountDict[key]
        account.append("%s:%s" % (key,value))
    account=(FIELD_DELIM.join(account))
    return account

def createPasswordFileBackups():
    #create password backup file
    try:
        passwordFile=filename=GlobalVariables.CLI_PASSWORD_FILE
        maxBackups=Settings().get(SETTING_MAX_PASSWORD_FILE_BACKUPS)
        if os.path.isfile(filename)==False:
            return
        currentBackup=maxBackups
        filenameTemplate="%s-v%s-%d"
        version=GlobalVariables.VERSION
        while currentBackup>0:
            backupFile= filenameTemplate % (passwordFile,version,currentBackup)
            if os.path.isfile(backupFile) == True:
                shutil.copy2(backupFile, filenameTemplate % (passwordFile,version,currentBackup+1))
            debug("Backup file: %s" % backupFile)
            currentBackup=currentBackup-1
        shutil.copy2(passwordFile, filenameTemplate % (passwordFile,version,1))
    except:
        printError("Password file back up failed.")
        error(fileOnly=True)

def modPrompt(field,defaultValue=None):
    promptStr=""
    if defaultValue==None:
      promptStr="%s: " % (field)
    else:
      promptStr="%s (%s): " % (field,defaultValue)
    n=prompt(promptStr)
    if n=="":
        n=defaultValue
    else:
        n=n.strip()
    return n


def multilinePrompt(promptString):
    return prompt (promptString)


def askAccountUsername(promptStr,defaultValue=None):

    print("User name generator is available. Type your username or type 'u' to generate username.")
    username=""
    if defaultValue!=None:
        username=defaultValue
    username=modPrompt (promptStr,username)
    while username=="u"  or username.startswith("C") or username.startswith("V"):
        if username=="u":
            username=generate_username("CVC-CVC",False)
        else:
            username=generate_username(username,False)
        username=modPrompt (promptStr,username)
    return username

def askAccountPassword(promptStr,infoText,defaultValue=None):
    print(infoText)
    if defaultValue==None:
        pwd=pwdPasswordWordLike()
        #pwd=pwdPassword()
    else:
        pwd=defaultValue
    pwd=modPrompt(promptStr,pwd)

    while pwd=="p":
        #if pwd=="p":
        pwd=pwdPasswordWordLike()
        #pwd=pwdPassword()
        pwd=modPrompt(promptStr,pwd)

    if pwd=='c':
        return defaultValue

    return pwd
