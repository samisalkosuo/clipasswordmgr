# -*- coding: utf-8 -*-

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
#
#template for commands

#copy this to new file and rename
#

from ..utils.utils import *
from .SuperCommand import *
from ..globals import *
from ..utils.settings import Settings


class PasswordCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
        #TODO: add to settings
        try:
          self.defaultFormat=Settings().get(SETTING_DEFAULT_PASSWORD_FORMAT)
        except:
          self.defaultFormat="CVCV/cvcv/nnnn/AAAA"
    
    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="pwd",description='Generate password using characters a-z,A-Z and 0-9.')
        cmd_parser.add_argument('-l','--length',metavar='LENGTH', required=False, type=int, default=12, help='Password length. Default is 12.')
        cmd_parser.add_argument('-t','--total',metavar='NR', required=False, type=int, default=1, help='Total number of passwords to generate.')
        cmd_parser.add_argument('-w','--wordlike', required=False, action='store_true', help='Use password format like words.')
        cmd_parser.add_argument('-f','--format', metavar='FORMAT', type=str, nargs='?', default=self.defaultFormat, help='Format for password like words: C=consonant, V=vowel, N=number, +=space, /=slash. Default is %s.' % self.defaultFormat)

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):

        pwdlen=self.cmd_args.length
        for i in range(self.cmd_args.total):
            if self.cmd_args.wordlike:
                pwd=pwdPasswordWordLike(self.cmd_args.format)
            else:
                pwd=pwdPassword(pwdlen)
            print(pwd)
        
        copyToClipboard(pwd,infoMessage="Password copied to clipboard.",account="",clipboardContent="generated password")

