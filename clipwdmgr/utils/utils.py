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

#Some common functions
import os
from datetime import datetime
import time
import argparse
import random

from .settings import Settings
from ..globals import *

#from: http://stackoverflow.com/a/14728477
class ArgumentParserError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

def parseCommandArgs(cmd_parser,inputList):
    '''Return tuple (cmd_args, help_for_help_command).
       If help then cmd_args is None, and if arg parsing succesfull help is None
       Exception in parsing, then both are None because error is printed/logged in this
       function
    '''
    #this is to get help text for internal help command
    if len(inputList)==2 and inputList[1]=="-HELP":
        return (None,(cmd_parser.format_usage().replace("usage:","").strip(),cmd_parser.description))

    try:
        cmd_args = cmd_parser.parse_args(inputList[1:])
        return (cmd_args,None)
    except ArgumentParserError as parser_error:
        print(parser_error)
        print(cmd_parser.format_usage().strip())
        #print(cmd_parser.description)
        return (None, None)
    except SystemExit as parser_error:
        #ignore system exit errors
        debug(parser_error)
        return (None,None)


def findMaxKeyLength(dictionary):
    maxLen=0
    for key in dictionary.keys():
        if len(key)>maxLen:
            maxLen=len(key)
    return maxLen

def printDictionary(dictionary,indent=""):
    formatString=getColumnFormatString(2,findMaxKeyLength(dictionary),delimiter=": ",align="<")
    keys=list(dictionary.keys())
    keys.sort()
    for key in keys:
        value=dictionary[key]
        if value==1:
            value="True"
        if value==0:
            value="False"
        valueType=type(value).__name__
        if valueType is not "str":
            value=str(value)
        print(indent+formatString.format(key,value))


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

def getCurrentTimestampString():
    return datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
    

def boolValue(value):
    string=str(value)
    return string.lower() in ("yes","y","true", "on", "t", "1")


def generate_username(formatStr,capitalize=True):
    """Generate random user name. formatStr is like CVC-CVC which generates username with consonant-vowel-consonant-consonant-vowel-consonant"""
    import random
    import re

    vowels="eyuioa"
    consonants="mnbvcxzlkjhgfdsptrwq"
    numbers="0123456789"

    def randomNumber():
        return random.choice(numbers)

    def randomVowel():
        return random.choice(vowels)

    def randomConsonant():
        return random.choice(consonants)

    regex = re.compile('[^a-zA-Z+]')
    formatStr=regex.sub('', formatStr)
    username=[]
    for c in formatStr.upper():
        if c=="C":
            username.append(randomConsonant())
        if c=="V":
            username.append(randomVowel())
        if c=="N":
            username.append(randomNumber())
        if c=="+":
            username.append(" ")
    username="".join(username)
    if capitalize==True:
        username= username.capitalize()

    return username

def generate_username_case_sensitive(formatStr):
    """Generate random user name. formatStr is like CVC-CVC which generates username with consonant-vowel-consonant-consonant-vowel-consonant.
    formatStr is case sensitive. """
    import random
    import re

    vowelsLower="eyuioa"
    consonantsLower="mnbvcxzlkjhgfdsptrwq"
    vowelsUpper="EYUIOA"
    consonantsUpper="MNBVCXZLKJHGFDSPTRWQ"
                     
    numbers="0123456789"

    def randomNumber():
        return random.choice(numbers)

    def randomVowelUpper():
        return random.choice(vowelsUpper)

    def randomConsonantUpper():
        return random.choice(consonantsUpper)

    def randomVowelLower():
        return random.choice(vowelsLower)

    def randomConsonantLower():
        return random.choice(consonantsLower)


    regex = re.compile('[^a-zA-Z+/]')
    formatStr=regex.sub('', formatStr)
    username=[]
    for c in formatStr:
        if c=="C":
            username.append(randomConsonantUpper())
        if c=="V":
            username.append(randomVowelUpper())
        if c=="c":
            username.append(randomConsonantLower())
        if c=="v":
            username.append(randomVowelLower())
        if c=="N":
            username.append(randomNumber())
        if c=="n":
            username.append(randomNumber())
        if c=="+":
            username.append(" ")
        if c=="/":
            username.append("/")
    username="".join(username)

    return username


def pwdPassword(length=12):
    chars="1234567890poiuytrewqasdfghjklmnbvcxzQWERTYUIOPLKJHGFDSAZXCVBNM"
    pwd=[]
    for i in range(length):
        pwd.append(random.choice(chars))
    return "".join(pwd)

def pwdPasswordWordLike(format="CVCV/cvcv/nnncC"):
    return generate_username_case_sensitive(format)


def copyToClipboard(stringToCopy,infoMessage=None,account=None,clipboardContent=None):
    if Settings().get(SETTING_ENABLE_CLIPBOARD_COPY)==True:

        if stringToCopy=="" or stringToCopy == None:
            print("Nothing to copy to clipboard.")
            return False

        cygwinClipboard="/dev/clipboard"
        if os.path.exists(cygwinClipboard):
            clipboardDevice = open(cygwinClipboard, "w")
            clipboardDevice.write(stringToCopy)
            if infoMessage != None:
                print(infoMessage)
            if account!=None and clipboardContent!=None:
                GlobalVariables.COPIED_TO_CLIPBOARD="%s of' %s'" % (clipboardContent,account)
        else:
            try:
                import pyperclip
                pyperclip.copy(stringToCopy)
                GlobalVariables.REAL_CONTENT_OF_CLIPBOARD=stringToCopy
                if infoMessage != None:
                    print(infoMessage)
                if account!=None and clipboardContent!=None:
                    if account!='':
                        GlobalVariables.COPIED_TO_CLIPBOARD="%s of '%s'" % (clipboardContent,account)
                    else:
                        GlobalVariables.COPIED_TO_CLIPBOARD="%s" % (clipboardContent)
                        
            except:
                print("Error copying to clipboard.")
    
    return True

def getClipboardText():
    try:
        import pyperclip
        text=pyperclip.paste()
        return text
    except:
        print("Error accessing clipboard.")
        return "-"

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

def setAccountFieldsToClipboard(row):
    pwd=row[COLUMN_PASSWORD]
    #set last account viewed variables
    #to to be used with keyboard shortcuts
    GlobalVariables.LAST_ACCOUNT_VIEWED_NAME=row[COLUMN_NAME]
    GlobalVariables.LAST_ACCOUNT_VIEWED_USERNAME=row[COLUMN_USERNAME]
    GlobalVariables.LAST_ACCOUNT_VIEWED_URL=row[COLUMN_URL]
    GlobalVariables.LAST_ACCOUNT_VIEWED_PASSWORD=row[COLUMN_PASSWORD]
    GlobalVariables.LAST_ACCOUNT_VIEWED_EMAIL=row[COLUMN_EMAIL]
    GlobalVariables.LAST_ACCOUNT_VIEWED_COMMENT=row[COLUMN_COMMENT]
    GlobalVariables.LAST_ACCOUNT_VIEWED_ID=row[COLUMN_ID]

    if Settings().getBoolean(SETTING_COPY_PASSWORD_ON_VIEW)==True:
        print()
        copyToClipboard(pwd,infoMessage="Password copied to clipboard.",account=row[COLUMN_NAME],clipboardContent="password")
