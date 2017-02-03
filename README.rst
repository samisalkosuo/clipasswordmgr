Command Line Password Manager
=============================

Command Line Password Manager is a tool to manage accounts/passwords in the command line. 
All accounts/passwords are stored in an encrypted file, protected by user given passphrase.

Encryption/decryption is done using Python cryptography library: https://cryptography.io/en/latest/.

Requirements
------------

CLI Password Manager requires Python 3.4.3 (or later). Python packages *cryptography* and *pyperclip* are required. Command line password generator, *pwgen* (http://sourceforge.net/projects/pwgen/), is not required but recommended.

Use environment variable CLIPWDMGR_FILE to specify path and file of your password file.
There is no default location for password file, so you need to specify it before executing
clipwdmgr. Reason for this is that password file could be in Dropbox or other directory
and shared across many computers.

Development and testing has been done using Windows 7 & Cygwin (64bit) and latest OS X & Brew.


Install
-------

Install latest version: **pip install clipwdmgr**.

or do it in steps (to avoid known problems):

- Install pyperclip: **pip install pyperclip**
- Install cryptography: **pip install cryptography**
- Install clipwdmgr: **pip install clipwdmgr**

**Known problem: Mac OS X**

When using Mac OS X El Capitan: install may fail with error: *fatal error: 'openssl/aes.h' file not found*.
Fix this by first installing OpenSSL using Homebrew and executing command::

	env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip install cryptography

and then using: *pip install clipwdmgr*

Or, specifying only binary for cryptography **pip install clipwdmgr --only-binary cryptography** should work too.

See here: https://github.com/pyca/cryptography/issues/2350.

**Known problem: MS Windows**

When using pip install in Windows and Cygwin, install may fail to with error: *error: Setup script exited with error: Unable to find vcvarsall.bat*.

Workaround is to install prereq cryptography before clipwdmgr: **pip install cryptography**. Specifying only binary for cryptography **pip install clipwdmgr --only-binary cryptography** may also work.

Usage
-----

Execute clipwdmgr and a simple shell opens. Start by adding new account using 'add' command.

Type 'help' to get list of available commands.
Commands include: add, view, search, edit, list, pwd, pwgen and others.

Shell is very basic but serves it's purpose. When you have added accounts you can view them using::

	view startofaccountname

View-command takes the start of account name and prints out all matching accounts and copies password
to clipboard.

Search-command searches all accounts by name, url or comment::

	search partofname


List-command lists all accounts::

	list


About
-----

Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
and some other words about v0.4 http://sami.salkosuo.net/cli-password-manager-v0-4/.
