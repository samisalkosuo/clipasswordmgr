clipasswordmgr
==============

Command Line Password Manager is a tool to manage passwords in the command line. All accounts/passwords are stored in an encrypted file, protected by user given passphrase.

Encryption/decryption is done using Python cryptography library: https://cryptography.io/en/latest/

## Install

CLI Password Manager requires Python3, so that must be installed.

- Download the files, at minimum clipwdmgr.py.
- Install mandatory prereq (cryptography): pip install cryptography.
- Optional: install prereq (pyperclip): pip install pyperclip.
- Optional: install command line password generator: pwgen
- Use environment variable CLIPWDMGR_FILE to specify path and file of your password
  file.

## Usage

Execute clipasswordmgr.py and a shell opens. Start by adding new account using 'add' command.

Type 'help' to get list of available commands:
```
CLI Password Manager v0.4
Copyright (C) 2015 by Sami Salkosuo.
Licensed under the MIT License.

Commands:
   add              [<name>]                                                         Add new account.
   alias            [<name> <cmd> <cmdargs>]                                         View aliases or create alias named 'name' for command 'cmd'.
   changepassphrase                                                                  Change passphrase.
   config           [<key>=<value>]                                                  List available configuration or set config values.
   copy             <start of name> | [pwd | uid | email | url | comment]            Copy value of given field of account to clipboard. Default is pwd.
   delete           <start of name>                                                  Delete account(s) that match given string.
   exit                                                                              Exit program.
   help                                                                              This help.
   info                                                                              Information about the program.
   list             [<start of name>]                                                Print all accounts or all that match given start of name.
   modify           <start of name>                                                  Modify account(s) that match given string.
   pwd                                                                               Generate 12-character (using a-z,A-Z and 0-9) password using simple generator.
   pwgen            [<pwgen opts and args>]                                          Generate password(s) using pwgen.
   search           <string in name or comment> | username=<string> | email=<string> Search accounts that have matching string.
   view             <start of name>                                                  View account(s) details.                                                           
```
                                                              
Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
