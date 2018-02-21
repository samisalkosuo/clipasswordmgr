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
#uname-command

from ..utils.utils import *
from .SuperCommand import *
from ..globals import *
from ..utils.settings import Settings

class UserNameCommand(SuperCommand):

    def __init__(self,cmd_handler):
        super().__init__(cmd_handler)
    

    def parseCommandArgs(self,userInputList):
        cmd_parser = ThrowingArgumentParser(prog="uname",description='Generate random username using given format.')
        cmd_parser.add_argument('-t','--total',metavar='NR', required=False, type=int, default=1, help='Total number of usernames to generate.')
        cmd_parser.add_argument('-c','--casesensitive', required=False, action='store_true', help='Format string is case sensitive (upper case V results upper case vowel and so on).')

        defaultUsernameFormat=Settings().get(SETTING_DEFAULT_UNAME_FORMAT)
        cmd_parser.add_argument('format',metavar='FORMAT', type=str, nargs='?', default=defaultUsernameFormat, help='Username format: C=consonant, V=vowel, N=number, +=space. Default is: %s.' % defaultUsernameFormat)

        (self.cmd_args,self.help_text)=parseCommandArgs(cmd_parser,userInputList)

    def execute(self):
        
        formatStr=self.cmd_args.format
        N=self.cmd_args.total
        for i in range(N):
            if self.cmd_args.casesensitive:
                pwd=generate_username_case_sensitive(formatStr)
            else:
                pwd=generate_username(formatStr,False)
            print(pwd)
