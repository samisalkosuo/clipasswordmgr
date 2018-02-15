Command Line Password Manager
=============================

Command Line Password Manager is a tool to manage accounts/passwords in the command line. 
All accounts/passwords are stored in an encrypted file, protected by user given passphrase.

Encryption/decryption is done using Python cryptography library: https://cryptography.io/en/latest/.

Requirements
------------

CLI Password Manager requires Python 3.6.4 (or later, but previous Python 3 versions might work too).
Python packages *prompt-toolkit*, *cryptography* and *pyperclip* are required. 

Environment variable CLIPWDMGR_DATA_DIR must be present and it must point to a directory that is
used to save password file and settings file.
Set CLIPWDMGR_DATA_DIR to Dropbox or other similar directory and you can use CLI Password Manager
across many computers.

Note to Windows-users: 
- use cmder or conemu because prompt-toolkit might work better than the standard command window.
- prompt-toolkit in Cygwin does not work correctly.


Install
-------

Not yet available from PyPI (Python Package Index).

Installation steps:

- **pip install cryptography**
- **pip install pyperclip**
- **pip install https://github.com/jonathanslenders/python-prompt-toolkit/archive/2.0.zip**
- **pip install https://github.com/samisalkosuo/clipasswordmgr/archive/master.zip**

pip-installation creates executable: **clipwdmgr**.

You can also use CLI Password Manager from GitHub source:

- **git clone https://github.com/samisalkosuo/clipasswordmgr**
- cd to clipasswordmgr and **python clipwdmgr-runner.py**

Usage
-----

Using CLI Password Manager is as simple as using any shell.

- When starting the program, passphrase is asked.
- Type 'help' to get list of available commands.
- Add new account using 'add' command.
- List all accounts using 'list' command.
- View an account using 'view' command.
- When viewing an account, password is copied to clipboard. This is very handy :-).
- Commands have options and help. For example: 'view -h' and 'copy -h'.
- Command history and completion is available.
- See help for more.

All accounts are stored to a password file in CLIPWDMGR_DATA_DIR directory. All accounts
are encrypted using your own passphrase.


About
-----

Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
and some other words about v0.4 http://sami.salkosuo.net/cli-password-manager-v0-4/.


Possible problems
-----------------

These problems were encountered when using v0.11. May apply to v0.12 and later as well.

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

