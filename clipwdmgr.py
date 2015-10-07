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
#Install prereqs using pip (or pip3):
#  pip3 install cryptography
#  pip3 install pyperclip
#
#
#Some design choices:
#   developed with Python 3 on Windows 7 & Cygwin-x64 and OS X
#   only one source file
#   store password in encrypted text file
#   runtime: use sqlite in-memory to work with accounts
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
VERSION="0.6"
COPYRIGHT="Copyright (C) 2015 by Sami Salkosuo."
LICENSE="Licensed under the MIT License."

PROMPTSTRING="pwdmgr>"

KEY=None

FIELD_DELIM="|||::|||"

#sqlite database
DATABASE=None
#sqlite database cursor
DATABASE_CURSOR=None
#columns for ACCOUNTS table and also fields in account string
COLUMN_NAME="NAME"
#CREATED column uniquely identifies account, highly unlikely that two accounts are created at the same time :-)
COLUMN_CREATED="CREATED"
COLUMN_UPDATED="UPDATED"
COLUMN_USERNAME="USERNAME"
COLUMN_URL="URL"
COLUMN_EMAIL="EMAIL"
COLUMN_PASSWORD="PASSWORD"
COLUMN_COMMENT="COMMENT"
DATABASE_ACCOUNTS_TABLE_COLUMNS=[COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT]
DATABASE_ACCOUNTS_TABLE_COLUMN_IS_TIMESTAMP=[COLUMN_CREATED,COLUMN_UPDATED]

#this is to display account info 
COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY=[COLUMN_NAME,COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT]

#environment variable that holds password file path and name
CLIPWDMGR_FILE="CLIPWDMGR_FILE"

CLI_PASSWORD_FILE=os.environ.get(CLIPWDMGR_FILE)

#configuration
CFG_MASKPASSWORD="MASKPASSWORD"
CFG_COLUMN_LENGTH="COLUMN_LENGTH"
CFG_COPY_PASSWORD_ON_VIEW="COPY_PASSWORD_ON_VIEW"
CFG_MASKPASSWORD_IN_VIEW="MASKPASSWORD_IN_VIEW"
CFG_PWGEN_DEFAULT_OPTS_ARGS="PWGEN_DEFAULT_OPTS_ARGS"
CFG_MAX_PASSWORD_FILE_BACKUPS="MAX_PASSWORD_FILE_BACKUPS"
CFG_ALIASES="ALIASES"
CFG_SAVE_CMD_HISTORY="SAVE_COMMAND_HISTORY"
CFG_HISTORY="HISTORY"
#defaults
CONFIG={
    CFG_MASKPASSWORD:True,
    CFG_COPY_PASSWORD_ON_VIEW:True,
    CFG_MASKPASSWORD_IN_VIEW:False,
    CFG_COLUMN_LENGTH:10,
    CFG_PWGEN_DEFAULT_OPTS_ARGS:"-cns1 12 1",
    CFG_MAX_PASSWORD_FILE_BACKUPS:10,
    CFG_SAVE_CMD_HISTORY:True,
    CFG_ALIASES:{},
    CFG_HISTORY:[]
    }

#configuration stored as json in home dir
CONFIG_FILE="%s/.clipwdmgr.cfg" % (expanduser("~"))

DEBUG=False

#command line args
args=None

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='Command Line Password Manager.')
    parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
    parser.add_argument('-f','--file', nargs=1,metavar='FILE', help='Passwords file.')
    parser.add_argument('-d','--decrypt', nargs=1, metavar='STR',help='Decrypt single account string.')
    parser.add_argument('-v,--version', action='version', version="%s v%s" % (PROGRAMNAME, VERSION))
    global args
    args = parser.parse_args()

#============================================================================================
#main function
def main():
    print("%s v%s" % (PROGRAMNAME, VERSION))
    print()

    if args.file:
        global CLI_PASSWORD_FILE
        CLI_PASSWORD_FILE=args.file[0]

    if CLI_PASSWORD_FILE==None:
        print("%s environment variable missing." % CLIPWDMGR_FILE)
        print("Use %s environment variable to set path and name of the password file." % CLIPWDMGR_FILE)
        sys.exit(1) 
    
    debug("command line args: %s" % args)


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
    #TODO: curses based shell with command history, completion, etc
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
        aliases=CONFIG[CFG_ALIASES]
        if cmd in aliases.keys():
            newCmd="%s %s" % (aliases[cmd]," ".join(inputList[1:]))
            callCmd(newCmd)
        else:
            print("%s not implemented." % cmd)
    else:
        #TODO: save to command history
        if userInput.find("history")==-1 and CONFIG[CFG_SAVE_CMD_HISTORY]==True:
            history=CONFIG[CFG_HISTORY]
            history.append(userInput)
            saveConfig()
        function(inputList)

#============================================================================================
#implemented commands

def aliasCommand(inputList):
    """
    [<name> <cmd> <cmdargs>]||View aliases or create alias named 'name' for command 'cmd cmdargs'.
    """
    aliases=CONFIG[CFG_ALIASES]
    if(len(inputList)==1):
        #list aliases
        for alias in sorted(aliases.keys()):
            print("%s='%s'" % (alias,aliases[alias]))
    else:
        #create new alias
        alias=inputList[1]
        cmd=inputList[2:]
        aliases[alias]=" ".join(cmd)
        saveConfig()

def historyCommand(inputList):
    """
    [<index> [c] | clear]||View history, execute command or clear entire history. 'c' after index copies command to clipboard.
    """
    history=CONFIG[CFG_HISTORY]
    if(len(inputList)==1):
        #list history
        i=0
        for cmd in history:
            print("%d: %s" % (i,cmd))
            i=i+1
    if(len(inputList)==2):
        arg=inputList[1]
        if arg=="clear":
            CONFIG[CFG_HISTORY]=[]
            saveConfig()
        else:
            cmd=history[int(arg)]
            callCmd(cmd)
    if(len(inputList)==3):
        arg=inputList[1]
        cmd=history[int(arg)]
        copyToClipboard(cmd)
        print("Command: '%s' copied to clipboard." % cmd)

def infoCommand(inputList):
    """
    ||Information about the program.
    """

    size=os.path.getsize(CLI_PASSWORD_FILE)
    formatString=getColumnFormatString(2,25,delimiter=": ",align="<")
    print(formatString.format("CLI_PASSWORD_FILE",CLI_PASSWORD_FILE))
    print(formatString.format("Password file size",sizeof_fmt(size)))

    loadAccounts()
    totalAccounts=(DATABASE_CURSOR.execute("select count(*) from accounts").fetchone()[0])
    print(formatString.format("Total accounts",str(totalAccounts)))
    lastUpdated=(DATABASE_CURSOR.execute("select updated from accounts order by updated desc").fetchone()[0])
    print(formatString.format("Last updated",lastUpdated))
    
    print(formatString.format("Config file",CONFIG_FILE))
    print("Configuration:")
    configList("  ")
    print("Aliases:")
    #list aliases
    aliases=CONFIG[CFG_ALIASES]
    for alias in aliases.keys():
        print("  %s='%s'" % (alias,aliases[alias]))

def addCommand(inputList):
    """
    [<name>]||Add new account.
    """
    debug("entering addCommand")
    loadAccounts()
    name=None
    if len(inputList)==2:
        name=inputList[1]
    if name is not None:
        print("Name     : %s" % name)
    else:
        name=prompt ("Name     : ")
        while name == "":
            print("Empty name not accepted")
            name=prompt ("Name     : ")
    URL=prompt ("URL      : ")
    username=prompt ("User name: ")
    email=prompt("Email    : ")
    
    #TODO: refactor asking password in here and in editCommand
    print("Password generator is available. Type your password or type 'p'/'ps' to generate password.")
    pwd=pwgenPassword()
    pwd=modPrompt("Password ",pwd)
    while pwd=="p" or pwd=="ps":
        if pwd=="p":
            pwd=pwgenPassword()
        if pwd=="ps":
            pwd=pwgenPassword(["-sy","12","1"])
        pwd=modPrompt("Password ",pwd)

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
    accountString=makeAccountString(newAccount)
    debug(accountString)

    createPasswordFileBackups()
    insertAccountToFile(accountString)

    print("Account added.")


def encryptCommand(inputList):
    """
    <start of name> [passphrase]||Encrypt selected accounts(s).
    """
    debug("entering encryptCommand")
    if verifyArgs(inputList,0,[2,3])==False:
        return
    arg=inputList[1]
    debug("Arg: %s" % arg)
    loadAccounts()
    rows=executeSelect(DATABASE_ACCOUNTS_TABLE_COLUMNS,arg)
    key=KEY
    if len(inputList)==3:
        key=createKey(inputList[2])
    for row in rows:
        name=row[COLUMN_NAME]
        print("%s: %s" % (name,encryptAccountRow(row,key)))
        

def decryptCommand(inputList):
    """
    <encrypted string> [passphrase]||Decrypt given string.
    """
    debug("entering decryptCommand")
    if verifyArgs(inputList,0,[2,3])==False:
        return
    arg=inputList[1]
    key=KEY
    if len(inputList)==3:
        key=createKey(inputList[2])
    print(decryptString(key,arg))


def selectCommand(inputList):
    """
    [<rest of select SQL>]||Execute SELECT SQL and print results as columns.
    """
    debug("entering selectCommand")
    if(len(inputList)==1):
        #show help
        formatString=getColumnFormatString(2,20,delimiter=": ",align="<")
        print(formatString.format("Table","ACCOUNTS"))
        print(formatString.format("Columns",",".join(DATABASE_ACCOUNTS_TABLE_COLUMNS)))
    else:
        loadAccounts()
        sql=" ".join(inputList)
        rows=DATABASE_CURSOR.execute(sql)
        columns=DATABASE_CURSOR.description
        columnNames=[]
        for c in columns:
            columnNames.append(c[0])
        formatString=getColumnFormatString(len(columnNames),CONFIG[CFG_COLUMN_LENGTH])
        headerLine=formatString.format(*columnNames)
        print(headerLine)
        for row in rows:
            values=[]
            for cname in columnNames:
                value=row[cname]
                if cname==COLUMN_PASSWORD and CONFIG[CFG_MASKPASSWORD]==True:
                    value="********"          
                values.append(shortenString(value))
            accountLine=formatString.format(*values)
            print(accountLine)

def listCommand(inputList):
    """
    [<start of name>]||Print all accounts or all that match given start of name.
    """
    loadAccounts()
    arg=""
    if(len(inputList)==2):
        arg=inputList[1]

    rows=executeSelect([COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],arg)
    printAccountRows(rows)

def deleteCommand(inputList):
    """
    <start of name>||Delete account(s) that match given string.
    """
    debug("entering deleteCommand")
    if verifyArgs(inputList,2)==False:
        return
    loadAccounts()
    arg=inputList[1]
    
    rows=list(executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg))
    for row in rows:
        printAccountRow(row)
        if boolValue(prompt("Delete this account (yes/no)? ")):
            sql="delete from accounts where %s=?" % (COLUMN_CREATED)
            DATABASE_CURSOR.execute(sql,(row[COLUMN_CREATED],))
            DATABASE.commit()
            saveAccounts()
            print("Account deleted.")

def editCommand(inputList):
    """
    <start of name>||Edit account(s) that match given string.
    """
    debug("entering editCommand")
    if verifyArgs(inputList,2)==False:
        return
    loadAccounts()
    arg=inputList[1]

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

            username=modPrompt("User name",row[COLUMN_USERNAME])
            values.append(username)

            email=modPrompt("Email",row[COLUMN_EMAIL])
            values.append(email)

            #if pwgenAvailable()==True:
            print("Password generator is available. Type your password or type 'p'/'ps' to generate password or 'c' to use original password.")
            originalPassword=row[COLUMN_PASSWORD]
            pwd=modPrompt("Password OLD: (%s) NEW:" % (originalPassword),originalPassword)
            while pwd=="p" or pwd=="ps" or pwd=="c":
                if pwd=="p":
                    pwd=pwgenPassword()
                if pwd=="ps":
                    pwd=pwgenPassword(["-sy","12","1"])
                if pwd=="c":
                    pwd=originalPassword
                pwd=modPrompt("Password OLD: (%s) NEW:" % (originalPassword),pwd)
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
            DATABASE_CURSOR.execute(sql,tuple(values))
            DATABASE.commit()
            saveAccounts()
            print("Account updated.")

def changepassphraseCommand(inputList):
    """
    ||Change passphrase.
    """
    debug("entering changepassphraseCommand")
    print("Not yet implemented.")
    newKey=askPassphrase("New passphrase: ")
    if newKey==None:
        return
    newKey2=askPassphrase("New passphrase again: ")
    if newKey!=newKey2:
        print("Passphrases do not match.")
        return

    loadAccounts()
    global KEY
    KEY=newKey
    saveAccounts()
    print ("Passphrase changed.")

def searchCommand(inputList):
    """
    <string in name,url or comment> | username=<string> | email=<string>||Search accounts that have matching string.
    """
    debug("entering searchCommand")
    if verifyArgs(inputList,2)==False:
        return
    loadAccounts()
    arg=inputList[1]
    where=""
    if arg.startswith("username="):
        arg=arg.replace("username=","")
        where="where %s like '%%%s%%' " % (COLUMN_USERNAME,arg)
    elif arg.startswith("email="):
        arg=arg.replace("email=","")
        where="where %s like '%%%s%%' " % (COLUMN_EMAIL,arg)
    else:
        where="where %s like '%%%s%%' or %s like '%%%s%%' or %s like '%%%s%%' " % (COLUMN_NAME,arg,COLUMN_COMMENT,arg,COLUMN_URL,arg)

    rows=executeSelect([COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],whereClause=where)
    printAccountRows(rows)

def copyCommand(inputList):
    """
    <start of name> | (pwd | uid | email | url | comment)||Copy value of given field of account to clipboard. Default is pwd.
    """
    if verifyArgs(inputList,None,[2,3])==False:
        return

    #TODO: more fine grained when selecting account, make it similar to view
    fieldToCopy=COLUMN_PASSWORD
    fieldName="Password"
    if len(inputList)==3:
        tocp=inputList[2]    
        if tocp=="pwd":
            fieldToCopy=COLUMN_PASSWORD
            fieldName="Password"
        if tocp=="uid":
            fieldToCopy=COLUMN_USERNAME
            fieldName="User name"
        if tocp=="email":
            fieldToCopy=COLUMN_EMAIL
            fieldName="Email"
        if tocp=="url":
            fieldToCopy=COLUMN_URL
            fieldName="URL"
        if tocp=="comment":
            fieldToCopy=COLUMN_COMMENT
            fieldName="Comment"

    loadAccounts()
    arg=inputList[1]

    rows=executeSelect([COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],arg)
    for row in rows:
        #printAccountRow(row)
        name=row[COLUMN_NAME]
        f=row[fieldToCopy]
        copyToClipboard(f)
        if f=="":
            print("%s: %s is empty." % (name,fieldName))
        else:
            print("%s: %s copied to clipboard." % (name,fieldName))


def viewCommand(inputList):
    """
    <start of name> [username=<string>] [comment=<string>]||View account(s) details that start with given string and have matching username and/or comment.
    """
    debug("entering viewCommand")
    if verifyArgs(inputList,0,[2,3,4])==False:
        return

    loadAccounts()
    arg=inputList[1]
    where="where name like \"%s%%\"" % arg
    for input in inputList[2:]:
        fields=["username","comment"]
        for field in fields:
            fe=field+"="
            if input.find(fe)>-1:
                where=where+" and %s like '%%%s%%'" % (field,input.replace(fe,""))
        #has username
    rows=executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg,whereClause=where)
    for row in rows:
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
    if verifyArgs(inputList,0,[1,2])==False:
        return
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

def pwdCommand(inputList):
    """
    [length]||Generate password using simple generator with characters a-z,A-Z and 0-9. Default length is 12.
    """
    pwdlen=12
    if(len(inputList)==2):
        pwdlen=int(inputList[1])
    print(pwdPassword(pwdlen))

def pwgenCommand(inputList):
    """
    [<pwgen opts and args>]||Generate password(s) using pwgen.
    """
    debug("entering pwgenCommand")
    if pwgenAvailable()==True:
        pwds=pwgenPassword(inputList[1:])
        print(pwds)
    else:
        print ("pwgen is not available. No passwords generated.")

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
#functions

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

    createNewFile(CLI_PASSWORD_FILE,accounts)


def encryptAccountRow(row,key=None):
    #create string of account and encrypt
    account=[]
    for columnName in row.keys():
        value=row[columnName]
        if value is not None:
            value=value.strip()
        account.append("%s:%s" % (columnName,value))
    if key==None:
        key=KEY
    return encryptString(key,FIELD_DELIM.join(account))

def printAccountRows(rows):
    #print account rows in columns
    #used by list and search commands 
    formatString=getColumnFormatString(6,CONFIG[CFG_COLUMN_LENGTH])
    headerLine=formatString.format(COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT)
    print(headerLine)
    for row in rows:
        pwd=row[COLUMN_PASSWORD]
        if CONFIG[CFG_MASKPASSWORD]==True:
            pwd="********"          
        pwd=shortenString(pwd)
        accountLine=formatString.format(shortenString(row[COLUMN_NAME]),shortenString(row[COLUMN_URL]),shortenString(row[COLUMN_USERNAME]),shortenString(row[COLUMN_EMAIL]),pwd,shortenString(row[COLUMN_COMMENT]))
        print(accountLine)

def makeAccountString(accountDict):
    account=[]
    for key in accountDict:
        value=accountDict[key]
        account.append("%s:%s" % (key,value))
    account=(FIELD_DELIM.join(account))
    return account

def getPassword():
    pwd=""
    print("Password generated. Type your password or type 'p'/'ps' to generate new password.")
    pwd=pwgenPassword()
    pwd2=prompt("Password (%s): " % pwd)
    debug("pwd2: %s (%d)" % (pwd2,len(pwd2)))
    while pwd2.lower()=="p" or pwd2.lower()=="ps":
        if pwd2=="p":
            pwd2=pwgenPassword()
        if pwd2=="ps":
            pwd2=pwgenPassword(["-sy","12","1"])
        pwd2=prompt("Password (%s): " % pwd2)
    if pwd2!="":
        pwd=pwd2

    return pwd

def printAccountRow(row):
    formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
    print("===============================")# % (name))
    #fields=[COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_COMMENT]

    for field in row.keys():#fields:
        value=row[field]
        if field==COLUMN_PASSWORD and CONFIG[CFG_MASKPASSWORD_IN_VIEW]==True:
            value="********"          
        print(formatString.format(field,value))

def shortenString(str):
    if len(str)>CONFIG[CFG_COLUMN_LENGTH]:
        str="%s..." % str[0:CONFIG[CFG_COLUMN_LENGTH]-3]
    return str

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

def verifyArgs(inputList,numberOfArgs,listOfAllowedNumberOfArgs=None):
    ilen=len(inputList)
    debug("len(inputList): %d" % ilen)
    correctNumberOfArgs=False
    if listOfAllowedNumberOfArgs!=None and ilen in listOfAllowedNumberOfArgs:
        correctNumberOfArgs=True
    else:
        correctNumberOfArgs=ilen == numberOfArgs
    if not correctNumberOfArgs:
        cmdName=inputList[0].lower()
        cmd="%sCommand" % cmdName
        func=globals().get(cmd)
        (args,desc)=getDocString(func)
        print("Wrong number of arguments.")
        print("Usage: %s %s" % (cmdName, args))
        return False
    return True

def modPrompt(field,defaultValue):
    n=prompt("%s (%s): " % (field,defaultValue))
    if n=="":
        n=defaultValue
    else:
        n=n.strip()
    return n

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

def configList(indent=""):
    formatString=getColumnFormatString(2,findMaxKeyLength(CONFIG),delimiter=": ",align="<")
    for key in sorted(CONFIG.keys()):
        if key is not CFG_ALIASES and key is not CFG_HISTORY:
            value=CONFIG[key]
            if value==1:
                value="True"
            if value==0:
                value="False"
            valueType=type(value).__name__
            if valueType is not "str":
                value=str(value)
            print(indent+formatString.format(key,value))

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

def pwgenAvailable():
    try:
        subprocess.check_output(["pwgen"])
        return True
    except:
        print("pwgen is not available.")
        return False

def pwgenPassword(argList=None):
    pwd=""

    if pwgenAvailable():
        cmd=["pwgen"]
        if argList is None or len(argList)==0:
            argList=CONFIG[CFG_PWGEN_DEFAULT_OPTS_ARGS].split()
        for arg in argList:
            cmd.append(arg)
        pwd=subprocess.check_output(cmd)
        pwd=pwd.decode("utf-8").strip()
    else:
        pwd=pwdPassword()

    return pwd

def pwdPassword(length=12):
    chars="1234567890poiuytrewqasdfghjklmnbvcxzQWERTYUIOPLKJHGFDSAZXCVBNM"
    pwd=[]
    for i in range(length):
        pwd.append(random.choice(chars))
    return "".join(pwd)

def versionInfo():
    print("%s v%s" % (PROGRAMNAME, VERSION))
    print(COPYRIGHT)
    print(LICENSE)

def createPasswordFileBackups():
    try:
        passwordFile=filename=CLI_PASSWORD_FILE
        maxBackups=CONFIG[CFG_MAX_PASSWORD_FILE_BACKUPS]
        if os.path.isfile(filename)==False:
            return
        currentBackup=maxBackups
        filenameTemplate="%s-v%s-%d"
        while currentBackup>0:
            backupFile= filenameTemplate % (passwordFile,VERSION,currentBackup)
            if os.path.isfile(backupFile) == True:
                shutil.copy2(backupFile, filenameTemplate % (passwordFile,VERSION,currentBackup+1))
            debug("Backup file: %s" % backupFile)
            currentBackup=currentBackup-1
        shutil.copy2(passwordFile, filenameTemplate % (passwordFile,VERSION,1))
    except:
        printError("Password file back up failed.")
        error(fileOnly=True)

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
    key=createKey(passphrase)
    #passphrase=hashlib.sha256(passphrase.encode('utf-8')).digest()
    #passphrase=base64.urlsafe_b64encode(passphrase)
    return key

def createKey(str):
    key=hashlib.sha256(str.encode('utf-8')).digest()
    key=base64.urlsafe_b64encode(key)
    return key

def encryptString(key,str):
    if str==None or str=="":
        return
    fernet = Fernet(key)
    encryptedString = fernet.encrypt(str.encode("utf-8"))
    return encryptedString.decode("utf-8")

def decryptString(key,str):
    if str==None or str=="":
        return
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
    for column in DATABASE_ACCOUNTS_TABLE_COLUMNS:
        sql.append(" ")
        sql.append(column)
        sql.append(" TEXT ")
        if column in DATABASE_ACCOUNTS_TABLE_COLUMN_IS_TIMESTAMP:
            sql.append(" DEFAULT CURRENT_TIMESTAMP ")
        else:
            sql.append(" DEFAULT '' ")
        sql.append(",")
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

def executeSelect(listOfColumnNames,whereNameStartsWith=None,whereClause=None,orderBy=COLUMN_NAME,returnSQLOnly=False):
    where=""
    if whereNameStartsWith is not None:
        where="where name like \"%s%%\"" % whereNameStartsWith
    if whereClause is not None:
        where=whereClause
    cols=",".join(listOfColumnNames)
    orderClause=""
    if orderBy is not None:
        orderClause="order by %s" % orderBy
    sql="select %s from accounts %s %s" % (cols,where,orderClause)
    debug("executeSelect SQL: %s" % sql)
    if returnSQLOnly==True:
        return sql
    else:
        return DATABASE_CURSOR.execute(sql)

def insertAccountToDB(accountString):
    accountDict=accountStringToDict(accountString)
    columnNames=[]
    values=[]
    qmarks=[]
    for key in accountDict.keys():            
        value=accountDict[key]
        if value is not "":
            columnNames.append(key)
            values.append(value)
            qmarks.append("?")
    sql=[]

    sql.append("insert into accounts (")
    sql.append(",".join(columnNames))
    sql.append(") values (")
    sql.append(",".join(qmarks))
    sql.append(")")
    sql="".join(sql)
    #debug("SQL: %s" % sql)
    #debug(tuple(values))
    DATABASE_CURSOR.execute(sql,values)

def insertAccountToFile(accountString):
    encryptedAccount=encryptString(KEY,accountString)
    appendStringToFile(CLI_PASSWORD_FILE,encryptedAccount)

#import accounts to database
def loadAccounts():
    if os.path.isfile(CLI_PASSWORD_FILE) == False:
        print("No accounts. Add accounts using add-command.")
        return

    accounts=readFileAsList(CLI_PASSWORD_FILE)
    for account in accounts:
        if account==None or account=="":
            continue
        decryptedAccount=decryptString(KEY,account)
        insertAccountToDB(decryptedAccount)

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
    file=open(filename,"w",encoding="utf-8")
    file.write("\n".join(lines))
    file.close()
    if fileExisted:
        debug("File overwritten: %s" % filename)
    else:
        debug("Created new file: %s" % filename)

def appendToFile(filename, lines=[]):
    file=open(filename,"a",encoding="utf-8")
    file.write("\n")
    file.write("\n".join(lines))
    file.close()

def appendStringToFile(filename, str):
    file=open(filename,"a",encoding="utf-8")
    file.write("\n")
    file.write(str)
    file.close()

def readFileAsString(filename):
    file=open(filename,"r",encoding="utf-8")
    lines=[]
    for line in file:
        lines.append(line)
    file.close()
    return "".join(lines)

def readFileAsList(filename):
    file=open(filename,"r",encoding="utf-8")
    lines=[]
    for line in file:
        lines.append(line.strip())
    file.close()
    return lines

def sizeof_fmt(num, suffix='B'):
    #from http://stackoverflow.com/a/1094933
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def toHexString(byteStr):
    return ''.join(["%02X" % ord(x) for x in byteStr]).strip()

def prompt(str):
    #inputStr=""
    #try:
    inputStr = input(str)
    #except KeyboardInterrupt:
    #    pass

    #inputStr=unicode(inputStr,"UTF-8")
    return inputStr

def debug(str):
    if DEBUG==True:
        msg="[DEBUG] %s: %s" % (datetime.now(),str)
        print(msg)

def printError(str):
    print("[ERROR]: %s" % str)

def error(fileOnly=False):
    import traceback
    str=traceback.format_exc()
    print(str)

def currentTimeMillis():
    return int(round(time.time() * 1000))

def currentTimestamp():
    return time.time()

def formatTimestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def boolValue(value):
    string=str(value)
    return string.lower() in ("yes","y","true", "on", "t", "1")

if __name__ == "__main__": 
    parseCommandLineArgs()
    debug("START")
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except:
        error()
    debug("END")
