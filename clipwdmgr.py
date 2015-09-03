#!/usr/bin/env python3

#CLI Password Manager
#
#The MIT License (MIT)
#
#Copyright (c) 2015 Sami Salkosuo
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
#Requires:
#   cryptography https://cryptography.io/en/latest/
#   pyperclip https://github.com/asweigart/pyperclip
#
#Developed with Python 3.4.3 on Windows 7 & Cygwin-x64 and OS X Yosemite
#
#Some design choices:
#   only one source file
#   store password in encrypted text file
#   use sqlite in-memory to work with accounts
#
#Some words about the origins of CLI Password Manager: 
#http://sami.salkosuo.net/cli-password-manager/

from datetime import datetime
from os.path import expanduser
from cryptography.fernet import Fernet
import sys
import os
import json
import hashlib
import base64
import shutil
import time
import sqlite3
import shlex
import argparse
import subprocess
import random

#global variables
PROGRAMNAME="CLI Password Manager"
VERSION="0.4"
COPYRIGHT="Copyright (C) 2015 by Sami Salkosuo."
LICENSE="Licensed under the MIT License."

PROMPTSTRING="pwdmgr>"
DEBUG=False
ERROR_FILE="clipwdmgr_error.log"
DEBUG_FILE="clipwdmgr_debug.log"

KEY=None

FIELD_DELIM="|||::|||"

#sqlite database
DATABASE=None
#sqlite database cursor
DATABASE_CURSOR=None
#columns for ACCOUNTS table
COLUMN_NAME="NAME"
COLUMN_CREATED="CREATED"
COLUMN_UPDATED="UPDATED"
COLUMN_USERNAME="USERNAME"
COLUMN_URL="URL"
COLUMN_EMAIL="EMAIL"
COLUMN_PASSWORD="PASSWORD"
COLUMN_COMMENT="COMMENT"
DATABASE_ACCOUNTS_TABLE_COLUMNS=[COLUMN_NAME,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_USERNAME,COLUMN_URL,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT]
DATABASE_ACCOUNTS_TABLE_COLUMN_IS_TIMESTAMP=[COLUMN_CREATED,COLUMN_UPDATED]#" DEFAULT '' "," DEFAULT CURRENT_TIMESTAMP "," DEFAULT CURRENT_TIMESTAMP "," DEFAULT '' "," DEFAULT '' "," DEFAULT '' "," DEFAULT '' "," DEFAULT '' "]
#environment variable that holds password file path and name
CLIPWDMGR_FILE="CLIPWDMGR_FILE"

CLI_PASSWORD_FILE=os.environ.get(CLIPWDMGR_FILE)
if CLI_PASSWORD_FILE==None:
    print("%s environment variable missing." % CLIPWDMGR_FILE)
    print("Use %s environment variable to set path and name of the password file." % CLIPWDMGR_FILE)
    sys.exit(1) 

#configuration
CFG_MASKPASSWORD="MASKPASSWORD"
CFG_COLUMN_LENGTH="COLUMN_LENGTH"
CFG_COPY_PASSWORD_ON_VIEW="COPY_PASSWORD_ON_VIEW"
#configuration stored as text file in home dir
#defaults
CONFIG={
    CFG_MASKPASSWORD:True,
    CFG_COPY_PASSWORD_ON_VIEW:True,
    CFG_COLUMN_LENGTH:10
    }

CONFIG_FILE="%s/.clipwdmgr.cfg" % (expanduser("~"))

#TODO:
#make backups of password file with version info
#CLI_PASSWORD_FILE="%s-%s.txt" % (CLI_PASSWORD_FILE,VERSION)

#TODO: check whether file exists and whether previous version file exists
#        if os.path.isfile(configFile) == False:


#command line args
args=None

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='Command Line Password Manager.')
    parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
    parser.add_argument('-f','--file', nargs=1, help='Password file.')
    parser.add_argument('-d','--decrypt', nargs=1, help='Decrypt single account.')
    parser.add_argument('-n','--new', action='store_true', help='Create new password file if -f file does not exist.')
    parser.add_argument('--migrate', action='store_true', help='Migrate passwords from version 0.3.')
    parser.add_argument('--debug', action='store_true', help='Show debug info.')
    parser.add_argument('--version', action='version', version="%s v%s" % (PROGRAMNAME, VERSION))
    global args
    global DEBUG
    args = parser.parse_args()
    DEBUG=args.debug

#============================================================================================
#main function
def main():
    print("%s v%s" % (PROGRAMNAME, VERSION))
    print()
    if DEBUG:
        print("DEBUG is True")
    
    debug("command line args: %s" % args)

    if args.migrate:
        migrate()
        return

    global KEY
    KEY=askPassphrase("Passphrase (CTRL-C to quit): ")
    if KEY==None:
        raise RuntimeError("Empty key not supported.")
        
    if args.decrypt:
        account=args.decrypt[0]
        print(decryptString(KEY,account))

        return

    if args.cmd:
        #execute given commands
        cmds=args.cmd
        debug("commands: %s" % cmds)
        for cmd in cmds:        
            openDatabase()
            try:
                debug("Calling %s..." % cmd)
                callCmd(cmd)
            except:
                error()
            closeDatabase()
        return

    loadConfig()
    #shell
    userInput=prompt(PROMPTSTRING)
    while userInput!="exit":
        openDatabase()
        try:
            debug("Input: %s" %userInput)
            callCmd(userInput)
        except:
            error()
        closeDatabase()
        userInput=prompt(PROMPTSTRING)

def callCmd(userInput):
    inputList=shlex.split(userInput)
    if len(inputList)==0:
        return
    if inputList[0].lower()=="select":
        inputList=userInput.split(" ")
    debug("User input: [%s]" %  ','.join(inputList))
    debug("User input len: [%d]" %  len(inputList))
    cmd=inputList[0].lower()
    functionName = "%sCommand" % cmd
    debug("Function name: %s" % functionName)
    #call command
    function = globals().get(functionName)
    if not function:
        #check alias
        print("%s not implemented." % cmd)
    else:
        function(inputList)

#============================================================================================
#implemented commands

def aliasCommand(inputList):
    """
    [<name> <cmd>]||View aliases or create alias named 'name' for command 'cmd'.
    """
    print("Not yet implemented")
    

def listCommand(inputList):
    """
    [<start of name>]||Print all accounts or all that match given start of name.
    """
    loadAccounts()
    where=""
    if(len(inputList)==2):
        where="where name like \"%s%%\"" % inputList[1]

    sql="select %s,%s,%s,%s,%s,%s from accounts %s order by %s" % (COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT,where,COLUMN_NAME)
    debug("SQL: %s" % sql)
    
    formatString=getColumnFormatString(6,CONFIG[CFG_COLUMN_LENGTH])
    headerLine=formatString.format(COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT)
    print(headerLine)
    for row in DATABASE_CURSOR.execute(sql):
        pwd=row[COLUMN_PASSWORD]
        if CONFIG[CFG_MASKPASSWORD]==True:
            pwd="********"          
        pwd=shortenString(pwd)
        accountLine=formatString.format(shortenString(row[COLUMN_NAME]),shortenString(row[COLUMN_URL]),shortenString(row[COLUMN_USERNAME]),shortenString(row[COLUMN_EMAIL]),pwd,shortenString(row[COLUMN_COMMENT]))
        print(accountLine)

def viewCommand(inputList):
    """
    <start of name>||View account(s) details.
    """
    debug("entering viewCommand")
    if verifyArgs(inputList,2)==False:
        return

    loadAccounts()
    arg=inputList[1]
    
    where="where name like \"%s%%\"" % arg
    sql="select %s,%s,%s,%s,%s,%s,%s,%s from accounts %s order by %s" % (COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT,where,COLUMN_NAME)
    debug("SQL: %s" % sql)
    formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
    for row in DATABASE_CURSOR.execute(sql):
        printAccountRow(row)
        pwd=row[COLUMN_PASSWORD]
        if CONFIG[CFG_COPY_PASSWORD_ON_VIEW]==True:
            print()
            copyToClipboard(pwd)
            print("Password copied to clipboard.")


def configCommand(inputList):
    """
    [<key>=<value>]||List available configuration or set config values.
    """
    if(len(inputList)==2):
        cmd=inputList[1]
        if cmd.find("=")>-1:
            keyValue=cmd.split("=")
            configSet(keyValue[0],keyValue[1])
        else:
            print("%s not recognized" % cmd)
    else:
        #list current config
        configList()


def exitCommand(inputList):
    """||Exit program."""
    pass


def helpCommand(inputList):
    """||This help."""
    debug("entering helpCommand")
    versionInfo()
    print()
    print("Commands:")
    names=[]
    for _n in globals().keys():
        names.append(_n)
    debug(names)
    names.sort()
    maxLenName=0
    maxLenArgs=0
    maxLenDesc=0
    commandList=[]
    for name in names:
        if name.endswith("Command"):
            cmdName=name.replace("Command","").lower()
            func=globals().get(name)
            (args,desc)=getDocString(func)
            if len(cmdName)>maxLenName:
                maxLenName=len(cmdName)
            if len(args)>maxLenArgs:
                maxLenArgs=len(args)
            if len(desc)>maxLenDesc:
                maxLenDesc=len(desc)
            commandHelp=[cmdName,args,desc]
            commandList.append(commandHelp)
    formatStringName=getColumnFormatString(1,maxLenName,delimiter=" ",align="<")
    formatStringArgs=getColumnFormatString(1,maxLenArgs,delimiter=" ",align="<")
    formatStringDesc=getColumnFormatString(1,maxLenDesc,delimiter=" ",align="<")

    for c in commandList:
        print("  ",formatStringName.format(c[0]),formatStringArgs.format(c[1]),formatStringDesc.format(c[2]))

#============================================================================================
#utility functions

def printAccountRow(row):
    formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
    name=row[COLUMN_NAME]
    print("===============================")# % (name))
    print(formatString.format(COLUMN_NAME,name))
    #print "========== %s ==========" % name
    url=row[COLUMN_URL]
    print(formatString.format(COLUMN_URL,url))
    username=row[COLUMN_USERNAME]
    print(formatString.format(COLUMN_USERNAME,username))
    email=row[COLUMN_EMAIL]
    print(formatString.format(COLUMN_EMAIL,email))
    pwd=row[COLUMN_PASSWORD]
    print(formatString.format(COLUMN_PASSWORD,pwd))
    timestamp = row[COLUMN_CREATED]
    print(formatString.format(COLUMN_CREATED,timestamp))
    timestamp = row[COLUMN_UPDATED]
    print(formatString.format(COLUMN_UPDATED,timestamp))
    comment=row[COLUMN_COMMENT]
    print(formatString.format(COLUMN_COMMENT,comment))

def shortenString(str):
    if len(str)>CONFIG[CFG_COLUMN_LENGTH]:
        str="%s..." % str[0:CONFIG[CFG_COLUMN_LENGTH]-3]
    return str

def accountLine(account,maxColumnLength,formatString):
    desc=account[JSONKEY_COMMENT]
    if len(desc)>maxColumnLength:
        desc="%s..." % desc[0:maxColumnLength-3]
    line=formatString.format(account[JSONKEY_NAME],account[JSONKEY_USERNAME],account[JSONKEY_EMAIL],account[JSONKEY_PWD],desc)
    return line

def getColumnFormatString(numberOfColumns,columnLength,delimiter="|",align="^"):
    header="{{:%s{ln}}}" % align
    columns=[]
    i=0
    while i < numberOfColumns:
        columns.append(header)
        i=i+1
    formatString=delimiter.join(columns).format(ln=columnLength)
    debug("Format string: %s" % formatString)
    return formatString

def verifyArgs(inputList,numberOfArgs):
    ilen=len(inputList)
    debug("len(inputList): %d" % ilen)
    if ilen != numberOfArgs:
        cmdName=inputList[0].lower()
        cmd="%sCommand" % cmdName
        func=globals().get(cmd)
        (args,desc)=getDocString(func)
        print("Wrong number of arguments.")
        print("Usage: %s %s" % (cmdName, args))
        return False
    return True


def loadConfig():
    #load config to sqlite database, if db not exists load defaults
    #if exists, set CONFIG dict from values in db

    if os.path.isfile(CONFIG_FILE) == False:
        saveConfig()
    else:
        global CONFIG
        f=open(CONFIG_FILE,"r")
        config=json.load(f)
        for key in config.keys():
            value=config[key]
            CONFIG[key]=value
        f.close()

def saveConfig():
    f=open(CONFIG_FILE,"w")
    json.dump(CONFIG,f)
    f.close()

def configList():
    formatString=getColumnFormatString(2,findMaxKeyLength(CONFIG),delimiter=": ",align="<")
    for key in sorted(CONFIG.keys()):
        value=CONFIG[key]
        print(formatString.format(key,value))

def configSet(key,value):
    #set config to dict
    global CONFIG
    key=key.upper()
    oldValue=CONFIG[key]
    valueType=type(oldValue).__name__
    if valueType=="int":
        value=int(value)
    if valueType=="bool":
        value=boolValue(value)
    CONFIG[key]=value
    saveConfig()

def versionInfo():
    print("%s v%s" % (PROGRAMNAME, VERSION))
    print(COPYRIGHT)
    print(LICENSE)

def getDocString(commandFunc):
    #return tuple from command function
    docString=commandFunc.__doc__
    args=""
    desc=""
    debug("Parsing %s" % commandFunc)
    if docString is not None:
        try:
            docString=docString.strip()
            doc=docString.split("||")
            args=doc[0].strip()
            desc=doc[1].strip()
        except:
            desc=docString
    else:
        desc="Not documented."
    return (args,desc)

def copyToClipboard(str):
    import pyperclip
    pyperclip.copy(str)

#============================================================================================
#encryption/decryption related functions

def askPassphrase(str):
    import getpass
    passphrase=getpass.getpass(str)
    if passphrase=="":
        return None
    passphrase=hashlib.sha256(passphrase.encode('utf-8')).digest()
    passphrase=base64.urlsafe_b64encode(passphrase)
    return passphrase

def encryptString(key,str):
    fernet = Fernet(key)
    encryptedString = fernet.encrypt(str.encode("utf-8"))
    return encryptedString.decode("utf-8")

def decryptString(key,str):
    fernet = Fernet(key)
    decryptedString = fernet.decrypt(str.encode("utf-8"))
    return decryptedString.decode("utf-8")


#============================================================================================
#database functions
def openDatabase():
    global DATABASE
    global DATABASE_CURSOR
    DATABASE=sqlite3.connect(':memory:')
    DATABASE.row_factory = sqlite3.Row
    DATABASE_CURSOR=DATABASE.cursor()
    sql=[]
    sql.append("CREATE TABLE accounts ")
    sql.append("(")
        #DATABASE_ACCOUNTS_TABLE_COLUMN_CONSTRAINTS
    for column in DATABASE_ACCOUNTS_TABLE_COLUMNS:
        sql.append(" ")
        sql.append(column)
        sql.append(" TEXT ")
        if column in DATABASE_ACCOUNTS_TABLE_COLUMN_IS_TIMESTAMP:
            sql.append(" DEFAULT CURRENT_TIMESTAMP ")
        else:
            sql.append(" DEFAULT '' ")
        sql.append(",")
    #sql.append(" TEXT, ".join(DATABASE_ACCOUNTS_TABLE_COLUMNS))
    #sql.append(" TEXT")
    sql=sql[:-1]
    sql.append(")")
    sql="".join(sql)
    debug("Create SQL: %s " %sql)
    DATABASE_CURSOR.execute(sql)

def closeDatabase():
    global DATABASE
    global DATABASE_CURSOR
    if DATABASE is not None:
        DATABASE.close()
    DATABASE=None
    DATABASE_CURSOR=None

#import accounts to database
def loadAccounts():
    accounts=readFileAsList(CLI_PASSWORD_FILE)
    for account in accounts:
        decryptedAccount=decryptString(KEY,account)
        accountDict=accountStringToDict(decryptedAccount)
        columnNames=[]
        values=[]
        qmarks=[]
        for key in accountDict.keys():            
            value=accountDict[key]
            if value is not "":
                columnNames.append(key)
                values.append(value)
                qmarks.append("?")
                #print("%s=%s" % (key,value))
        sql=[]
        sql.append("insert into accounts (")
        sql.append(",".join(columnNames))
        sql.append(") values (")
        sql.append(",".join(qmarks))
        sql.append(")")
        sql="".join(sql)
        debug("SQL: %s" % sql)
        debug(tuple(values))
        DATABASE_CURSOR.execute(sql,values)


def accountStringToDict(str):
    account=str.split(FIELD_DELIM)
    accountDict=dict()
    for field in account:
        ind=field.find(":")
        name=field[0:ind]
        value=field[ind+1:]
        accountDict[name]=value
        #print("%s == %s" % (name,value))
    return accountDict


#============================================================================================
#common functions

def findMaxKeyLength(dictionary):
    maxLen=0
    for key in dictionary.keys():            
        if len(key)>maxLen:
            maxLen=len(key)
    return maxLen

def createNewFile(filename, lines=[]):
    fileExisted=os.path.isfile(filename)
    file=open(filename,"w")
    file.write("\n".join(lines))
    file.close()
    if fileExisted:
        debug("File overwritten: %s" % filename)
    else:
        debug("Created new file: %s" % filename)

def appendToFile(filename, lines=[]):
    file=open(filename,"a")
    file.write("\n".join(lines))
    file.close()

def readFileAsString(filename):
    file=open(filename,"r")
    lines=[]
    for line in file:
        lines.append(line)
    file.close()
    return "".join(lines)

def readFileAsList(filename):
    file=open(filename,"r")
    lines=[]
    for line in file:
        lines.append(line.strip())
    file.close()
    return lines

def createFileBackups(filename,maxBackups):
    if os.path.isfile(filename)==False:
        return
    currentBackup=maxBackups
    while currentBackup>0:
        backupFile="%s.%d" % (passwordFile, currentBackup)
        if os.path.isfile(backupFile) == True:
            shutil.copy2(backupFile, '%s.%d' % (passwordFile,currentBackup+1))
        debug("Backup file: %s" % backupFile)
        currentBackup=currentBackup-1
    shutil.copy2(passwordFile, '%s.1' % passwordFile)

def toHexString(byteStr):
    return ''.join(["%02X" % ord(x) for x in byteStr]).strip()

def prompt(str):
    inputStr = input(str)
    #inputStr=unicode(inputStr,"UTF-8")
    return inputStr

def debug(str):
    if DEBUG:
        msg="%s: %s" % (datetime.now(),str)
        if DEBUG_FILE is not None:
            file=open(DEBUG_FILE,"a")
            file.write("%s\n" % msg)
            file.close()
        print(msg)

def printError(str):
    print("[ERROR]: %s" % str)

def error():
    import traceback
    str=traceback.format_exc()
    print(str)
    msg="%s: %s" % (datetime.now(),str)
    appendToFile(ERROR_FILE,[msg])

def currentTimeMillis():
    return int(round(time.time() * 1000))

def currentTimestamp():
    return time.time()

def formatTimestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def boolValue(value):
    string=str(value)
    return string.lower() in ("yes","y","true", "on", "t", "1")

#============================================================================================
#migrate functions
#to be removed in future version

def migrate():
    #migrate from v0.3
    import configparser
    homeDir = expanduser("~")
    CONFIG_FILE=".clipwdmgrcfg"
    configFile="%s/%s" % (homeDir,CONFIG_FILE)
    configParser = configparser.RawConfigParser()   
    configParser.read(r'%s' % configFile)
    passwordDir=configParser.get('config', 'password.file.dir')
    passwordFileName=configParser.get('config', 'password.file.name')

    #add version to default file name
    passwordFileName="%s-0.3.txt" % (passwordFileName)
    passwordFile="%s/%s" % (passwordDir,passwordFileName)
    print("v0.3 password file: %s" % passwordFile)
    key=askMigrateKey("Passphrase for v0.3 password file: ")
    pwdJSON=loadAccountsOld(key,passwordFile)
    accounts=[]
    for a in pwdJSON:
        account=[]
        for key in a:
            value=a[key]
            if key=="CREATED" or key=="UPDATED":
                value=formatTimestamp(float(a[key]))
            if key!="ID":
                account.append("%s:%s" % (key,value))
        #Add URL field
        account.append("URL:")
        accounts.append(FIELD_DELIM.join(account))
    #read accounts and store them to new text file, one account per line, all encrypted separately
    print("New password file: %s" % CLI_PASSWORD_FILE)
    key=askPassphrase("Passphrase for new password file: ")
    key2=askPassphrase("Passphrase for new password file (again): ")
    if key!=key2:
        printError("Passphrases do not match.")
        return
    encryptedAccounts=[]
    for account in accounts:
        encryptedAccounts.append(encryptString(key,account))
        #appendToFile("testfile.txt",[encryptedAccount])
        #print(encryptedAccount)
    createNewFile(CLI_PASSWORD_FILE,encryptedAccounts)

def askMigrateKey(str):
    import getpass
    passphrase=getpass.getpass(str)
    if passphrase=="":
        return None
    passphrase=hashlib.sha256(passphrase.encode('utf-8')).digest()
    key=base64.urlsafe_b64encode(passphrase)
    return key

def loadAccountsOld(key,passwordFile):
    jsonObj=loadJSONFile(key,passwordFile)
    #loadMetaConfig(jsonObj)
    JSON_ACCOUNTS='accounts'
    accounts=jsonObj[JSON_ACCOUNTS]
    #populateAccountsTable(accounts)
    return accounts

def loadJSONFile(key,passwordFile):
    fernet = Fernet(key)
    encryptedJSON=readFileAsString(passwordFile)
    jsonString=fernet.decrypt(encryptedJSON.encode("utf-8"))
    jsonObj=json.loads(jsonString.decode("utf-8"))
    return jsonObj

#end migrate functions
#============================================================================================

if __name__ == "__main__": 
    parseCommandLineArgs()
    debug("START")
    try:
        main()
    except KeyboardInterrupt:
        pass
    except:
        error()
    debug("END")
