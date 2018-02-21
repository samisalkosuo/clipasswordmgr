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

#set keybindings 

import webbrowser

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal

from ..globals import *
from .utils import *
from ..globals import GlobalVariables

def setKeyBindings():
    # set key bindings.
    
    bindings = KeyBindings()

    def copyTextToClipboard(textToCopy,contentDesc,printedDesc):
        accountName=GlobalVariables.LAST_ACCOUNT_VIEWED_NAME
        if copyToClipboard(textToCopy,infoMessage=None,account=accountName,clipboardContent=contentDesc):
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

    # Add open url in browser key binding.
    @bindings.add('c-c','c-o')
    def _(event):
        """
        Open URL in web browser
        """
        def openUrl():
            if GlobalVariables.LAST_ACCOUNT_VIEWED_URL == "" or GlobalVariables.LAST_ACCOUNT_VIEWED_URL == "-":
                print("Can not open empty URL.")
                return

            print("Opening URL '%s'..." % GlobalVariables.LAST_ACCOUNT_VIEWED_URL)
            webbrowser.open_new_tab(GlobalVariables.LAST_ACCOUNT_VIEWED_URL)

        run_in_terminal(openUrl)

    return bindings
