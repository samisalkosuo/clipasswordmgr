clipasswordmgr
==============

Command Line Password Manager is a tool to manage passwords in the command line. All accounts/passwords are stored in an encrypted file, protected by user given passphrase.

Encryption/decryption is done using Python cryptography library: https://cryptography.io/en/latest/.

## Install

CLI Password Manager requires Python 3.4.3 (or later), so that must be installed. 
Development/testing has been done using Windows 7 & Cygwin (64bit) and latest OS X & Brew.

- Download the files, at minimum clipwdmgr.py.
- Install mandatory prereq (cryptography): pip install cryptography.
- (Optional, but recommended) install prereq (pyperclip): pip install pyperclip.
- (Optional, but recommended) install command line password generator: pwgen.
- Use environment variable CLIPWDMGR_FILE to specify path and file of your password
  file.
- If you have used version 0.3, use --migrate option to migrate accounts to new file
  (this option was available in v0.4 & v0.5 and t was removed in v0.6).

## Usage

Execute clipwdmgr.py and a shell opens. Start by adding new account using 'add' command.

Type 'help' to get list of available commands:
```
CLI Password Manager v0.6
Copyright (C) 2015 by Sami Salkosuo.
Licensed under the MIT License.

Commands:
   add              [<name>]                                                             Add new account.
   alias            [<name> <cmd> <cmdargs>]                                             View aliases or create alias named 'name' for command 'cmd cmdargs'.
   changepassphrase                                                                      Change passphrase.
   config           [<key>=<value>]                                                      List available configuration or set config values.
   copy             <start of name> | (pwd | uid | email | url | comment)                Copy value of given field of account to clipboard. Default is pwd.
   delete           <start of name>                                                      Delete account(s) that match given string.
   exit                                                                                  Exit program.
   help                                                                                  This help.
   history          [<index> [c] | clear]                                                View history, execute command or clear entire history. 'c' after index copies command to clipboard.
   info                                                                                  Information about the program.
   list             [<start of name>]                                                    Print all accounts or all that match given start of name.
   modify           <start of name>                                                      Modify account(s) that match given string.
   pwd              [length]                                                             Generate password using simple generator with characters a-z,A-Z and 0-9. Default length is 12.
   pwgen            [<pwgen opts and args>]                                              Generate password(s) using pwgen.
   search           <string in name,url or comment> | username=<string> | email=<string> Search accounts that have matching string.
   select           [<rest of select SQL>]                                               Execute SELECT SQL and print results as columns.
   view             <start of name> [username=<string>] [comment=<string>]               View account(s) details that start with given string and have matching username and/or comment.
   ```
                                                              
Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
and other words about v0.4 http://sami.salkosuo.net/cli-password-manager-v0-4/.
