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

__version__="0.13"

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
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal

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

#key bindings
bindings=None

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

    clipboardText="-"
    if getClipboardText() == GlobalVariables.REAL_CONTENT_OF_CLIPBOARD:
        clipboardText=GlobalVariables.COPIED_TO_CLIPBOARD
    
    #programName="%s v%s" % (PROGRAMNAME, __version__)
    #return "%s. Clipboard: %s." % (programName,clipboardText)
    keyboardShortcuts=""
    if GlobalVariables.LAST_ACCOUNT_VIEWED_NAME != "-":
        #set keyboard shortcut help to toolbar if account have been viewed
        keyboardShortcuts="Keyboard shortcuts (see help): (C-c C-p) (C-c C-n) (...)."
    return "Clipboard: %s. %s" % (clipboardText,keyboardShortcuts)

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='Command Line Password Manager.')
    parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
    parser.add_argument('-f','--file', nargs=1,metavar='FILE', help='use given passwords file.')
    parser.add_argument('-d','--decrypt', nargs=1, metavar='STR',help='Decrypt single account string.')
    parser.add_argument('-v,--version', action='version', version="%s v%s" % (PROGRAMNAME, __version__))
    parser.add_argument('--passphrase', nargs=1, metavar='STR',help='Passphrase.')
    
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
            style=style,
            extra_key_bindings=bindings)
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

def initVariables():
    #init global variables
    GlobalVariables.COPIED_TO_CLIPBOARD="-"
    GlobalVariables.REAL_CONTENT_OF_CLIPBOARD="-"
    
    GlobalVariables.LAST_ACCOUNT_VIEWED_NAME="-"
    GlobalVariables.LAST_ACCOUNT_VIEWED_USERNAME="-"
    GlobalVariables.LAST_ACCOUNT_VIEWED_URL="-"
    GlobalVariables.LAST_ACCOUNT_VIEWED_PASSWORD="-"
    GlobalVariables.LAST_ACCOUNT_VIEWED_EMAIL="-"
    GlobalVariables.LAST_ACCOUNT_VIEWED_COMMENT="-"

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
    
    if args.passphrase:
        GlobalVariables.KEY=createKey(args.passphrase[0])
    else:
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

def setKeyBindings():
    # set key bindings.
    global bindings
    bindings = KeyBindings()

    def copyTextToClipboard(textToCopy,contentDesc,printedDesc):
        accountName=GlobalVariables.LAST_ACCOUNT_VIEWED_NAME
        copyToClipboard(textToCopy,infoMessage=None,account=accountName,clipboardContent=contentDesc)
        print("%s of '%s' copied to clipboard." % (printedDesc,accountName))
        

    # Add copy password key binding.
    @bindings.add('c-c','c-p')
    def _(event):
        """
        Copy password of last viewed account to clipboard
        """
        def copyText():
            copyTextToClipboard(GlobalVariables.LAST_ACCOUNT_VIEWED_PASSWORD,'password','Password')
        run_in_terminal(copyText)

    # Add copy password key binding.
    @bindings.add('c-c','c-n')
    def _(event):
        """
        Copy username of last viewed account to clipboard
        """
        def copyText():
            copyTextToClipboard(GlobalVariables.LAST_ACCOUNT_VIEWED_USERNAME,'user name','User name')
        run_in_terminal(copyText)

    # Add copy email key binding.
    @bindings.add('c-c','c-e')
    def _(event):
        """
        Copy email of last viewed account to clipboard
        """
        def copyText():
            copyTextToClipboard(GlobalVariables.LAST_ACCOUNT_VIEWED_EMAIL,'email','Email')
        run_in_terminal(copyText)

    # Add copy URL key binding.
    @bindings.add('c-c','c-u')
    def _(event):
        """
        Copy URL of last viewed account to clipboard
        """
        def copyText():
            copyTextToClipboard(GlobalVariables.LAST_ACCOUNT_VIEWED_URL,'URL','URL')
        run_in_terminal(copyText)

    # Add copy comment key binding.
    @bindings.add('c-c','c-c')
    def _(event):
        """
        Copy comment of last viewed account to clipboard
        """
        def copyText():
            copyTextToClipboard(GlobalVariables.LAST_ACCOUNT_VIEWED_COMMENT,'comment','Comment')
        run_in_terminal(copyText)

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
    
    initVariables()

    checkEnv()

    #print program & version when starting
    programName="%s v%s" % (PROGRAMNAME, __version__)
    print(programName)

    getKey()

    if args.file:
        #set specified password file
        GlobalVariables.CLI_PASSWORD_FILE=args.file[0]

    if executeCommandLineArgs() == False:
        #did not execute any command line args
        #start interface
        try:
            setKeyBindings()
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
