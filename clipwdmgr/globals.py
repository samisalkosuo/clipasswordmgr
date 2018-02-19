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

#settings filename
CLIPWDMGR_SETTINGS_FILE_NAME="clipwdmgr_settings.json"

#this is to display account info
COLUMNS_TO_SELECT_ORDERED_FOR_DISPLAY=[COLUMN_NAME,COLUMN_URL,COLUMN_CREATED,COLUMN_UPDATED,COLUMN_USERNAME,COLUMN_EMAIL,COLUMN_PASSWORD,COLUMN_COMMENT]

#Settings key names

SETTING_DEFAULT_COLUMN_WIDTH="default_column_width"
SETTING_DEFAULT_UNAME_FORMAT="default_username_format"
SETTING_MASK_PASSWORD="mask_password"
SETTING_MASK_PASSWORD_ON_VIEW="mask_password_on_view"
SETTING_COPY_PASSWORD_ON_VIEW="copy_password_to_clipboard"
SETTING_MAX_PASSWORD_FILE_BACKUPS="max_password_file_backups"
SETTING_ENABLE_CLIPBOARD_COPY="enable_clipboard_copy"
#settings default values, if setting file does not exist
#these are saved to settings file
SETTING_DEFAULT_VALUES={
    SETTING_DEFAULT_COLUMN_WIDTH:15,
    SETTING_DEFAULT_UNAME_FORMAT:"CVCCVC",
    SETTING_MASK_PASSWORD:True,
    SETTING_MASK_PASSWORD_ON_VIEW:False,
    SETTING_COPY_PASSWORD_ON_VIEW:True,
    SETTING_ENABLE_CLIPBOARD_COPY:True,
    SETTING_MAX_PASSWORD_FILE_BACKUPS:10
}


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
        
        #all these variables must be set before reading

        VERSION=None

        #password file and path
        CLI_PASSWORD_FILE=None

        #data dir, set via env variable
        CLIPWDMGR_DATA_DIR=None

        #encryption/decryption key, set when program starts
        KEY=None

        #what was copied to clipboard
        COPIED_TO_CLIPBOARD="n/a"
        REAL_CONTENT_OF_CLIPBOARD="n/a"

        #last account viewed
        LAST_ACCOUNT_VIEWED_NAME="-"
        LAST_ACCOUNT_VIEWED_USERNAME="-"
        LAST_ACCOUNT_VIEWED_URL="-"
        LAST_ACCOUNT_VIEWED_PASSWORD="-"
        LAST_ACCOUNT_VIEWED_EMAIL="-"
        LAST_ACCOUNT_VIEWED_COMMENT="-"

    def __str__(self): return self.val
