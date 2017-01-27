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

#Some common functions
import os
from datetime import datetime
import time
from .globals import *
import argparse

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

