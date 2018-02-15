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
#   prompt-toolkit https://github.com/jonathanslenders/python-prompt-toolkit
#
#Requires packages:
#  cryptography
#  pyperclip
#  prompt-toolkit
#

__version__="0.12"

import sys
import os
import json
import shutil
import shlex
import argparse
import subprocess
import random

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import set_title, CompleteStyle
from prompt_toolkit.contrib.completers import WordCompleter

from .globals import *
from .crypto.crypto import *
from .utils.utils import *
from .commands.CommandHandler import CommandHandler
from .globals import GlobalVariables



#command line args
args=None

#command history
cmdHistoryFile=FileHistory("%s/%s" % (os.environ.get(CLIPWDMGR_DATA_DIR),"cmd_history.txt"))
#command completer for prompt
cmdCompleter=None

#style for toolbar
style = Style.from_dict({
        'bottom-toolbar':      '#000000 bg:#ffffff',
        #'bottom-toolbar':      '#aaaa00 bg:#000000',
        #'bottom-toolbar.text': '#aaaa44 bg:#aa4444',
        #'bottom-toolbar':      '#000000 bg:#000000',
        #'bottom-toolbar.text': '#000000 bg:#000000',
    })

#toolbar
def bottom_toolbar():
    #return [('bottom-toolbar', ' This is a toolbar. ')]
    programName="%s v%s" % (PROGRAMNAME, __version__)
    return "%s. There will be cool info here." % programName

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='Command Line Password Manager.')
    parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
    parser.add_argument('-f','--file', nargs=1,metavar='FILE', help='use given passwords file.')
    parser.add_argument('-d','--decrypt', nargs=1, metavar='STR',help='Decrypt single account string.')
    parser.add_argument('-v,--version', action='version', version="%s v%s" % (PROGRAMNAME, __version__))
    global args
    args = parser.parse_args()

def error():
    import traceback
    print(traceback.format_exc())

def myPrompt():
    return prompt(PROMPTSTRING,
            history=cmdHistoryFile,
            completer=cmdCompleter,
            complete_while_typing=False,
            #complete_style=CompleteStyle.READLINE_LIKE,
            bottom_toolbar=bottom_toolbar, 
            style=style)
    #toolbar does not work when using cygwin

def main_clipwdmgr():
    programName="%s v%s" % (PROGRAMNAME, __version__)
    set_title(programName)

    #set version as global variable
    GlobalVariables.VERSION=__version__

    cmdHandler=CommandHandler()
    
    #set command completer
    global cmdCompleter
    cmdCompleter=WordCompleter(cmdHandler.cmdNameList)
    
    userInput=myPrompt()
    while userInput!="exit":
        try:
            if userInput != "":
                cmdHandler.execute(userInput)
        except:
            error()            
        userInput=myPrompt()


#============================================================================================
#main

#check if program data dir is set and exists
#exit if not set
def checkEnv():    
    dataDir=os.environ.get(CLIPWDMGR_DATA_DIR)
    if  dataDir == None:
        print("%s environment variable missing." % CLIPWDMGR_DATA_DIR)
        print("Set %s environment variable to the data directory of CLI Password Manager." % CLIPWDMGR_DATA_DIR)
        sys.exit(2)

    if os.path.isdir(dataDir) == False:
        print("%s does not exist or is not a directory." % dataDir)
        sys.exit(2)
    #set data dir
    GlobalVariables.CLIPWDMGR_DATA_DIR=dataDir
    #set password file variabe
    GlobalVariables.CLI_PASSWORD_FILE="%s/%s" %(dataDir,CLIPWDMGR_ACCOUNTS_FILE_NAME)

#get key to be used to encrypt and decrypt
def getKey():
    
    try:
        GlobalVariables.KEY=askPassphrase("Passphrase: ")
    except KeyboardInterrupt:
        sys.exit(1)
    
    if GlobalVariables.KEY==None:
        print("Empty passphrase is not allowed.")
        sys.exit(3)

#check command line args before starting the interface
def executeCommandLineArgs():

    if args.decrypt:
        account=args.decrypt[0]
        print(decryptString(GlobalVariables.KEY,account))
        return True

    if args.cmd:
        cmdHandler=CommandHandler()
        for cmd in args.cmd:
            print(">%s" % cmd)
            cmdHandler.execute(cmd)
            print()
        return True

    return False

def main():

    parseCommandLineArgs()
    try:        
        if args.help:
            #if help option, do nothing else
            return
    except AttributeError:
        #if no help, AttributeError is thrown
        #no problem, continue
        pass

    checkEnv()
    getKey()

    if args.file:
        #set specified password file
        GlobalVariables.CLI_PASSWORD_FILE=args.file[0]

    if executeCommandLineArgs() == False:
        #did not execute any command line args
        #start interface
        try:
            main_clipwdmgr()
        except KeyboardInterrupt:
            #thrown when ctrl-c
            #exit
            sys.exit(1)
        except SystemExit:
            sys.exit(1)
        except:
            error()


if __name__ == "__main__":
    main()
