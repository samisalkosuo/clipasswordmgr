#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#CLI Password Manager
#
#The MIT License (MIT)
#
#Copyright (c) 2015,2017 Sami Salkosuo
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
#
#Requires packages:
#  cryptography
#  pyperclip
#
#
#Some design choices:
#   developed with Python 3 on Windows 7 & Cygwin-x64 and OS X
#   store password in encrypted text file
#   runtime: use sqlite in-memory to work with accounts
#
#Some words about the origins of CLI Password Manager: 
#http://sami.salkosuo.net/cli-password-manager/

__version__="0.11"

import sys
import os
import json
import shutil
import shlex
import argparse
import subprocess
import random

from .globals import *
from .common import *
from .crypto import *
from .database import *

#command line args
args=None

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='Command Line Password Manager.')
    parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
    parser.add_argument('-f','--file', nargs=1,metavar='FILE', help='Passwords file.')
    parser.add_argument('-d','--decrypt', nargs=1, metavar='STR',help='Decrypt single account string.')
    parser.add_argument('-v,--version', action='version', version="%s v%s" % (PROGRAMNAME, __version__))
    global args
    args = parser.parse_args()

#============================================================================================
#main function
def main_clipwdmgr():
    print("%s v%s" % (PROGRAMNAME, __version__))
    print()

    if args.file:
        global CLI_PASSWORD_FILE
        CLI_PASSWORD_FILE=args.file[0]

    if CLI_PASSWORD_FILE==None:
        print("%s environment variable missing." % CLIPWDMGR_FILE)
        print("Use %s environment variable to set path and name of the password file." % CLIPWDMGR_FILE)
        print()
        print("For example: Set %s to DROPBOXDIR/clipwdmgr_accounts.txt " % CLIPWDMGR_FILE)
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
        cmd=inputList[0]
        aliases=CONFIG[CFG_ALIASES]
        if cmd in aliases.keys():
            newCmd="%s %s" % (aliases[cmd]," ".join(inputList[1:]))
            callCmd(newCmd)
        else:
            print("%s not implemented." % cmd)
    else:
        #save to command history
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

    cmd_parser = ThrowingArgumentParser(prog="alias",description='View or create command alias.')
    cmd_parser.add_argument('-n','--name', metavar='NAME',type=str,required=False, help='Alias name.')
    cmd_parser.add_argument('-c','--command-name', dest='command_name', metavar='CMD',type=str, required=False,help='Command name.')
    cmd_parser.add_argument('-d','--delete', required=False, action='store_true',help="Delete alias.")
    cmd_parser.add_argument('arguments', metavar='arg', type=str, nargs='*',
                    help="Command arguments. If command argument includes '-', surround it with '\"' and spaces (for example: \" -cn1s \").)")

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    aliases=CONFIG[CFG_ALIASES]
    if cmd_args.name==None:
        #list aliases
        for alias in sorted(aliases.keys()):
            print("%s='%s'" % (alias,aliases[alias]))
    else:
        alias=cmd_args.name
        if cmd_args.command_name is None and cmd_args.delete is False:
            print("-c, --command-name is required.")
            (tmp,help_text)=parseCommandArgs(cmd_parser,['alias','-HELP'])
            print("Usage: %s" % help_text[0])
            return
        else:
            if cmd_args.delete is not None:
                #delete alias
                del aliases[alias]
            else:
                #create new alias
                cmd=cmd_args.command_name
                args=cmd_args.arguments
                aliasCmd=[]
                aliasCmd.append(cmd)
                for carg in args:
                    aliasCmd.append(carg)
                aliasCmd=" ".join(aliasCmd)
                aliases[alias]=aliasCmd
            saveConfig()

def historyCommand(inputList):
    """
    [last | <index> [c] | clear]||View history, execute command or clear entire history. 'last' executes last command. 'c' after index copies command to clipboard.
    """

    cmd_parser = ThrowingArgumentParser(prog="history",description='View history, execute command or clear entire history.')
    cmd_parser.add_argument('-l','--last',required=False, nargs='?',default=0,metavar='INDEX', type=int, help='Execute last or last INDEXth command.')
    cmd_parser.add_argument('-c','--copy', required=False, action='store_true',help="Copy command to clipboard.")
    cmd_parser.add_argument('--clear', required=False, action='store_true',help="Clear history.")
    cmd_parser.add_argument('-r','--repeat', required=False, action='store_true',help="Repeat last command.")

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    history=CONFIG[CFG_HISTORY]
    if len(history)==0:
        print("No history to repeat.")
        return

    if cmd_args.clear==True:
        CONFIG[CFG_HISTORY]=[]
        saveConfig()
        return

    def __callCmd(index):
        cmd=history[index]
        callCmd(cmd)
        if cmd_args.copy==True:
            copyToClipboard(cmd,infoMessage="Command: '%s' copied to clipboard." % cmd)

    if cmd_args.repeat==True or (cmd_args.last==None and cmd_args.repeat==False):
        __callCmd(-1)
        return

    if cmd_args.last is not None and cmd_args.last > 0:
        __callCmd(cmd_args.last)
        return

    #if got this far, show history
    i=0
    for cmd in history:
        print("%d: %s" % (i,cmd))
        i=i+1


def infoCommand(inputList):
    """
    ||Information about the program.
    """
    cmd_parser = ThrowingArgumentParser(prog="info",description='Information about the program.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    size=os.path.getsize(CLI_PASSWORD_FILE)
    formatString=getColumnFormatString(2,25,delimiter=": ",align="<")
    print(formatString.format("Version",__version__))
    print(formatString.format("CLI_PASSWORD_FILE",CLI_PASSWORD_FILE))
    print(formatString.format("Password file size",sizeof_fmt(size)))

    loadAccounts(KEY)
    totalAccounts=selectFirst("select count(*) from accounts")
    print(formatString.format("Total accounts",str(totalAccounts)))
    lastUpdated=selectFirst("select updated from accounts order by updated desc")
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

    cmd_parser = ThrowingArgumentParser(prog="add",description='Add new account.')
    cmd_parser.add_argument('name',metavar='NAME', type=str, nargs=1, help='Account name.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    loadAccounts(KEY,"add")
    name=cmd_args.name[0]

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
    pwd=askAccountPassword("Password ","Password generator is available. Type your password or type 'p'/'ps' to generate password.")
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
    insertAccountToFile(KEY,accountString)

    print("Account added.")


def encryptCommand(inputList):
    """
    <start of name> [passphrase]||Encrypt selected accounts(s).
    """
    debug("entering encryptCommand")

    cmd_parser = ThrowingArgumentParser(prog="encrypt",description='Encrypt selected accounts(s).')
    cmd_parser.add_argument('-p','--passphrase', metavar='STR',help='Encryption passphrase.')
    cmd_parser.add_argument('-n','--nocopy', required=False, action='store_true',help="Do not copy encrypted string to clipboard.")
    cmd_parser.add_argument('accounts', metavar='account_name', type=str, nargs='+',
                    help='Account names, or beginning of account names, to encrypt.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    for arg in cmd_args.accounts:
        debug("Arg: %s" % arg)
        loadAccounts(KEY)
        rows=executeSelect(DATABASE_ACCOUNTS_TABLE_COLUMNS,arg)
        key=KEY
        if cmd_args.passphrase != None:
            key=createKey(cmd_args.passphrase)
        for row in rows:
            name=row[COLUMN_NAME]
            encryptedString=encryptAccountRow(row,key)
            print("%s: %s" % (name,encryptedString))
            if cmd_args.nocopy==False:
                copyToClipboard(encryptedString)

def decryptCommand(inputList):
    """
    <encrypted string> [passphrase]||Decrypt given string.
    """
    debug("entering decryptCommand")

    cmd_parser = ThrowingArgumentParser(prog="decrypt",description='Decrypt given string(s).')
    cmd_parser.add_argument('-p','--passphrase', metavar='STR',help='Decryption passphrase.')
    cmd_parser.add_argument('strings', metavar='str', type=str, nargs='+',
                    help='Decrypted strings.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    for arg in cmd_args.strings:
        key=KEY
        if cmd_args.passphrase != None:
            key=createKey(cmd_args.passphrase)
        print(decryptString(key,arg))


def selectCommand(inputList):
    """
    [<rest of select SQL>]||Execute SELECT SQL and print results as columns.
    """
    debug("entering selectCommand")

    cmd_parser = ThrowingArgumentParser(prog="select",description='Execute SELECT SQL statement and print results.')
    cmd_parser.add_argument('-i','--info', required=False, action='store_true',help="Accounts-table info.")
    cmd_parser.add_argument('statement', metavar='query_part', type=str, nargs='*',
                    help='Select SQL query parts.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    queryParts=cmd_args.statement
    if cmd_args.info==True or len(queryParts)==0:
        formatString=getColumnFormatString(2,20,delimiter=": ",align="<")
        print(formatString.format("Table","ACCOUNTS"))
        print(formatString.format("Columns",",".join(DATABASE_ACCOUNTS_TABLE_COLUMNS)))
        print()
        print("Example select-command:")
        print('  select * from accounts where email like "%acme.com"')
        return
    loadAccounts(KEY)
    sql="select %s" % (" ".join(queryParts))
    debug("SQL: %s" % sql)
    (rows,columns)=executeSql(sql)
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
    cmd_parser = ThrowingArgumentParser(prog="list",description='Print all accounts or all that match given start of name.')
    cmd_parser.add_argument('name', metavar='NAME', type=str, nargs='?',
                    help='Start of name.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    loadAccounts(KEY)
    arg=""
    if cmd_args.name:
        arg=cmd_args.name

    rows=executeSelect([COLUMN_NAME,COLUMN_URL,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],arg)
    printAccountRows(rows)

def deleteCommand(inputList):
    """
    <start of name>||Delete account(s) that match given string.
    """
    debug("entering deleteCommand")

    cmd_parser = ThrowingArgumentParser(prog="delete",description='Delete account(s) that match given string.')
    cmd_parser.add_argument('name', metavar='NAME', type=str, nargs=1,
                    help='Start of name.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    loadAccounts(KEY)
    arg=cmd_args.name[0]

    rows=list(executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg))
    for row in rows:
        printAccountRow(row)
        if boolValue(prompt("Delete this account (yes/no)? ")):
            sql="delete from accounts where %s=?" % (COLUMN_CREATED)
            executeDelete(sql,(row[COLUMN_CREATED],))
            saveAccounts()
            print("Account deleted.")

def editCommand(inputList):
    """
    <start of name>||Edit account(s) that match given string.
    """
    debug("entering editCommand")

    cmd_parser = ThrowingArgumentParser(prog="edit",description='Edit account(s) that match given string.')
    cmd_parser.add_argument('name', metavar='NAME', type=str, nargs=1,
                    help='Start of name.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    loadAccounts(KEY)
    arg=cmd_args.name[0]

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

def changepassphraseCommand(inputList):
    """
    ||Change passphrase.
    """
    debug("entering changepassphraseCommand")

    cmd_parser = ThrowingArgumentParser(prog="changepassphrase",description='Change passphrase.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    newKey=askPassphrase("New passphrase: ")
    if newKey==None:
        return
    newKey2=askPassphrase("New passphrase again: ")
    if newKey!=newKey2:
        print("Passphrases do not match.")
        return

    global KEY
    loadAccounts(KEY)
    KEY=newKey
    saveAccounts()
    print ("Passphrase changed.")

def searchCommand(inputList):
    """
    <string in name,url or comment> | username=<string> | email=<string>||Search accounts that have matching string.
    """
    debug("entering searchCommand")

    cmd_parser = ThrowingArgumentParser(prog="search",description='Search accounts that match given string.')
    group = cmd_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u','--username',metavar='UNAME', type=str, help='Search by username.')
    group.add_argument('-e','--email',metavar='EMAIL', type=str, help='Search by email.')
    group.add_argument('searchstring', metavar='STRING', type=str, nargs='?',
                    help='Search string in name, url or comment.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    loadAccounts(KEY)
    where=""

    arg=cmd_args.username
    if arg is not None:
        where="where %s like '%%%s%%' " % (COLUMN_USERNAME,arg)

    arg=cmd_args.email
    if arg is not None:
        where="where %s like '%%%s%%' " % (COLUMN_EMAIL,arg)

    arg=cmd_args.searchstring
    if arg is not None:
        where="where %s like '%%%s%%' or %s like '%%%s%%' or %s like '%%%s%%' " % (COLUMN_NAME,arg,COLUMN_COMMENT,arg,COLUMN_URL,arg)


    rows=executeSelect([COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],whereClause=where)
    printAccountRows(rows)

def copyCommand(inputList):
    """
    <start of name> | (pwd | uid | email | url | comment)||Copy value of given field of account to clipboard. Default is pwd.
    """
    debug("entering copyCommand")

    cmd_parser = ThrowingArgumentParser(prog="copy",description='Copy value of given field of account to clipboard.')
    group = cmd_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u','--username',action='store_true', help='Copy username to clipboard.')
    group.add_argument('-e','--email',action='store_true', help='Copy email to clipboard.')
    group.add_argument('-p','--password',action='store_true', help='Copy password to clipboard.')
    group.add_argument('-U','--url',action='store_true', help='Copy URL to clipboard.')
    group.add_argument('-c','--comment',action='store_true', help='Copy comment to clipboard.')

    cmd_parser.add_argument('account', metavar='NAME', type=str, nargs=1,
                    help='Account name.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    fieldToCopy=""
    fieldName=""
    if cmd_args.username==True:
        fieldToCopy=COLUMN_USERNAME
        fieldName="User name"
    if cmd_args.email==True:
        fieldToCopy=COLUMN_EMAIL
        fieldName="Email"
    if cmd_args.password==True:
        fieldToCopy=COLUMN_PASSWORD
        fieldName="Password"
    if cmd_args.url==True:
        fieldToCopy=COLUMN_URL
        fieldName="URL"
    if cmd_args.comment==True:
        fieldToCopy=COLUMN_COMMENT
        fieldName="Comment"

    loadAccounts(KEY)
    arg=cmd_args.account[0]

    rows=executeSelect([COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_NAME,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT],arg)
    for row in rows:
        #printAccountRow(row)
        name=row[COLUMN_NAME]
        f=row[fieldToCopy]
        if f=="":
            print("%s: %s is empty." % (name,fieldName))
        else:
            copyToClipboard(f,infoMessage="%s: %s copied to clipboard." % (name,fieldName))


def viewCommand(inputList):
    """
    <start of name> [username=<string>] [comment=<string>]||View account(s) details that start with given string and have matching username and/or comment.
    """
    debug("entering viewCommand")

    cmd_parser = ThrowingArgumentParser(prog="view",description='View account(s) details that start with given string and have matching username and/or comment.')
    cmd_parser.add_argument('-u','--username',metavar='UNAME', required=False, type=str, help='Account includes username.')
    cmd_parser.add_argument('-c','--comment',metavar='COMMENT', required=False, type=str, help='String in comment field.')
    cmd_parser.add_argument('-e','--encrypt', required=False, action='store_true', help='View account as encrypted string.')

    cmd_parser.add_argument('account', metavar='NAME', type=str, nargs=1,
                    help='Account name.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    loadAccounts(KEY)
    arg=cmd_args.account[0]

    where="where name like \"%s%%\"" % arg

    arg=cmd_args.username
    if arg:
        where=where+" and username like '%%%s%%'" % (arg)

    arg=cmd_args.comment
    if arg:
        where=where+" and comment like '%%%s%%'" % (arg)

    rows=executeSelect(COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY,arg,whereClause=where)
    for row in rows:
        if cmd_args.encrypt==True:
            encryptedAccount=encryptAccountRow(row)
            print(encryptedAccount)
            copyToClipboard(encryptedAccount,infoMessage="Encrypted account copied to clipboard.")
        else:
            printAccountRow(row)
            pwd=row[COLUMN_PASSWORD]
            if CONFIG[CFG_COPY_PASSWORD_ON_VIEW]==True:
                print()
                copyToClipboard(pwd,infoMessage="Password copied to clipboard.")

def configCommand(inputList):
    """
    [<key>=<value>]||List available configuration or set config values.
    """
    cmd_parser = ThrowingArgumentParser(prog="config",description='List configuration or set configuration values.')
    cmd_parser.add_argument('-k','--key',metavar='KEY', required=False, type=str, help='Config key name.')
    cmd_parser.add_argument('-v','--value',metavar='VALUE', required=False, type=str, help='Config value for key.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    if cmd_args.key==None and cmd_args.value==None:
        #list current config
        configList()
        return
    if bool(cmd_args.key) ^ bool(cmd_args.value):
        print('--key and --value are both required')
        return

    configSet(cmd_args.key,cmd_args.value)


def pwdCommand(inputList):
    """
    [length]||Generate password using simple generator with characters a-z,A-Z and 0-9. Default length is 12.
    """
    cmd_parser = ThrowingArgumentParser(prog="pwd",description='Generate password using characters a-z,A-Z and 0-9.')
    cmd_parser.add_argument('-l','--length',metavar='LENGTH', required=False, type=int, default=12, help='Password length. Default is 12.')
    cmd_parser.add_argument('-t','--total',metavar='NR', required=False, type=int, default=1, help='Total number of passwords to generate.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    pwdlen=cmd_args.length
    for i in range(cmd_args.total):
        pwd=pwdPassword(pwdlen)
        print(pwd)
    copyToClipboard(pwd,infoMessage="Password copied to clipboard.")

def pwgenCommand(inputList):
    """
    [<pwgen opts and args>]||Generate password(s) using pwgen.
    """
    debug("entering pwgenCommand")

    cmd_parser = ThrowingArgumentParser(prog="pwgen",description='Generate password(s) using pwgen.')
    cmd_parser.add_argument('options', metavar='opt', type=str, nargs='*',
                    help='Options/arguments for pwgen.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    options=[]
    for option in cmd_args.options:
        options.append(option.strip())

    if pwgenAvailable()==True:
        pwds=pwgenPassword(options)
        print(pwds)
        copyToClipboard(pwds,infoMessage="Password copied to clipboard.")
    else:
        print ("pwgen is not available. No passwords generated.")

def unameCommand(inputList):
    """
    [<format>]||Generate random username using given format. Format is string of C=consonants, V=vowels and N=numbers. Default format is CVCCVC.
    """
    cmd_parser = ThrowingArgumentParser(prog="uname",description='Generate random username using given format.')
    cmd_parser.add_argument('-t','--total',metavar='NR', required=False, type=int, default=1, help='Total number of usernames to generate.')
    cmd_parser.add_argument('format',metavar='FORMAT', type=str, nargs='?', default="CVCCVC", help='Username format: C=consonant, V=vowel, N=number, +=space. Default is: CVCCVC.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    formatStr=cmd_args.format
    N=cmd_args.total
    for i in range(N):
        pwd=generate_username(formatStr,False)
        print(pwd)


def exitCommand(inputList):
    """||Exit program."""
    cmd_parser = ThrowingArgumentParser(prog="exit",description='Exit program.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    pass

def helpCommand(inputList):
    """||This help."""
    debug("entering helpCommand")

    cmd_parser = ThrowingArgumentParser(prog="help",description='This help.')

    (cmd_args,help_text)=parseCommandArgs(cmd_parser,inputList)
    if help_text is not None:
        return help_text
    if cmd_args is None:
        return

    versionInfo()
    print()
    func=globals().get("infoCommand")
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
            (args,desc)=func([cmdName,"-HELP"])
            args=args.replace(cmdName,"").strip()
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
        pwd=pwgenPassword()
    else:
        pwd=defaultValue
    pwd=modPrompt(promptStr,pwd)

    while pwd=="p" or pwd=="ps":
        if pwd=="p":
            pwd=pwgenPassword()
        if pwd=="ps":
            pwd=pwgenPassword(["-sy","12","1"])
        pwd=modPrompt(promptStr,pwd)

    if pwd=='c':
        return defaultValue

    return pwd

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
    print("%s v%s" % (PROGRAMNAME, __version__))
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
            backupFile= filenameTemplate % (passwordFile,__version__,currentBackup)
            if os.path.isfile(backupFile) == True:
                shutil.copy2(backupFile, filenameTemplate % (passwordFile,__version__,currentBackup+1))
            debug("Backup file: %s" % backupFile)
            currentBackup=currentBackup-1
        shutil.copy2(passwordFile, filenameTemplate % (passwordFile,__version__,1))
    except:
        printError("Password file back up failed.")
        error(fileOnly=True)

def copyToClipboard(stringToCopy,infoMessage=None):
    if CONFIG[CFG_ENABLE_COPY_TO_CLIPBOARD]==True:
        cygwinClipboard="/dev/clipboard"
        if os.path.exists(cygwinClipboard):
            clipboardDevice = open(cygwinClipboard, "w")
            clipboardDevice.write(stringToCopy)
            if infoMessage != None:
                print(infoMessage)
        else:
            import pyperclip
            pyperclip.copy(stringToCopy)
            if infoMessage != None:
                print(infoMessage)

#============================================================================================
#main

def main():
    parseCommandLineArgs()
    debug("START")
    try:
        main_clipwdmgr()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except:
        error()
    debug("END")


if __name__ == "__main__":
    main()
