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

#encryption/decryption related functions
from cryptography.fernet import Fernet
import hashlib
import base64

def askPassphrase(str):
    import getpass
    passphrase=getpass.getpass(str)
    if passphrase=="":
        return None
    key=createKey(passphrase)
    #passphrase=hashlib.sha256(passphrase.encode('utf-8')).digest()
    #passphrase=base64.urlsafe_b64encode(passphrase)
    return key

def createKey(str):
    key=hashlib.sha256(str.encode('utf-8')).digest()
    key=base64.urlsafe_b64encode(key)
    return key

def encryptString(key,str):
    if str==None or str=="":
        return
    fernet = Fernet(key)
    encryptedString = fernet.encrypt(str.encode("utf-8"))
    return encryptedString.decode("utf-8")

def decryptString(key,str):
    if str==None or str=="":
        return
    fernet = Fernet(key)
    decryptedString = fernet.decrypt(str.encode("utf-8"))
    return decryptedString.decode("utf-8")



