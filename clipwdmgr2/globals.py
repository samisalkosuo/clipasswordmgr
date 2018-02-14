#The MIT License (MIT)
#
#Copyright (c) 2015,2016 Sami Salkosuo
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


#All global variables/constants
import os
from os.path import expanduser
from .clipwdmgr import __version__

#global constants
#variables are in the GlobalVariables singleton at the end of this file

PROGRAMNAME="CLI Password Manager"
COPYRIGHT="Copyright (C) 2015, 2018 by Sami Salkosuo."
LICENSE="Licensed under the MIT License."

def versionInfo():
    print("%s v%s" % (PROGRAMNAME, __version__))
    print(COPYRIGHT)
    print(LICENSE)

PROMPTSTRING="pwdmgr>"

FIELD_DELIM="|||::|||"

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


CLIPWDMGR_ACCOUNTS_FILE_NAME="clipwdmgr_accounts.txt"
#env variable name that holds data files like password file, cmd history, settings
CLIPWDMGR_DATA_DIR="CLIPWDMGR_DATA_DIR"
#file that holds accounts
#combines datadir and accounts file name
#CLI_PASSWORD_FILE=None

#this is to display account info
COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY=[COLUMN_NAME,COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT]

#environment variable that holds password file path and name
#CLIPWDMGR_FILE="CLIPWDMGR_FILE"

#CLI_PASSWORD_FILE=os.environ.get(CLIPWDMGR_FILE)

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
CFG_ENABLE_COPY_TO_CLIPBOARD="ENABLE_COPY_TO_CLIPBOARD"
#defaults
CONFIG={
    CFG_MASKPASSWORD:True,
    CFG_COPY_PASSWORD_ON_VIEW:True,
    CFG_MASKPASSWORD_IN_VIEW:False,
    CFG_COLUMN_LENGTH:10,
    CFG_PWGEN_DEFAULT_OPTS_ARGS:"-cns1 12 1",
    CFG_MAX_PASSWORD_FILE_BACKUPS:10,
    CFG_SAVE_CMD_HISTORY:True,
    CFG_ENABLE_COPY_TO_CLIPBOARD:True,
    CFG_ALIASES:{},
    CFG_HISTORY:[]
    }

#configuration stored as json in home dir
CONFIG_FILE="%s/.clipwdmgr.cfg" % (expanduser("~"))

DEBUG=False


#global variables singleton class to share global variables across
#many modules
#from http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html  
class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

#global variables singleton class to share global variables across
#many modules
class GlobalVariables(Borg):
    def __init__(self):
        Borg.__init__(self)
        CLI_PASSWORD_FILE=None
        VERSION=None
        #encryption/decryption key, set when program starts
        KEY=None


    def __str__(self): return self.val

