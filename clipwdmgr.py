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
#   store password in text file
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
import configparser 

#global variables
PROGRAMNAME="CLI Password Manager"
VERSION="0.4"
COPYRIGHT="Copyright (C) 2015 by Sami Salkosuo."
LICENSE="Licensed under the MIT License."

PROMPTSTRING="pwdmgr>"
DEBUG=False
ERROR_FILE="clipwdmgr_error.log"
DEBUG_FILE="clipwdmgr_debug.log"

#environment variable that holds password file path and name
CLIPWDMGR_FILE="CLIPWDMGR_FILE"

cliPasswordFile=os.environ.get(CLIPWDMGR_FILE)
if cliPasswordFile==None:
    print("%s environment variable missing." % CLIPWDMGR_FILE)
    print("Use %s environment variable to set path and name of the password file." % CLIPWDMGR_FILE)
    sys.exit(1) 

#command line args
args=None

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='Command Line Password Manager.')
    parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
    parser.add_argument('-f','--file', nargs=1, help='Password file.')
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

    #config()
    if args.migrate is not None:
        #migrate from v0.3
        #read accounts and store them to new text file, one account per line, all encrypted separately

        pass

    if args.cmd is not None:
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

    #shell
    userInput=prompt(PROMPTSTRING)
    while userInput!="exit":
    #    openDatabase()
        try:
            print("Input: %s" %userInput)
            #callCmd(userInput)
        except:
            error()
     #   closeDatabase()
        userInput=prompt(PROMPTSTRING)

#============================================================================================


#============================================================================================
#common functions

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

if __name__ == "__main__": 
    parseCommandLineArgs()
    debug("START")
    try:
        main()
    except:
        error()
    debug("END")
