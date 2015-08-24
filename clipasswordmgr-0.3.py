#!/usr/bin/python

#CLI Password Manager
#
#Copyright 2015 Sami Salkosuo
#http://sami.salkosuo.net
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#
#Requires:
#	cryptography https://cryptography.io/en/latest/
#	pyperclip https://github.com/asweigart/pyperclip
#
#Developed with Python 2.7.x on Windows 7 & Cygwin-x64 and OS X Yosemite
#
#Some design choices:
#	only one source file
#	store accounts as JSON and encrypt JSON file
#	read and decrypt file for each command when needed
#	use sqlite in-memory to work with accounts
#

from datetime import datetime
from os.path import expanduser
from cryptography.fernet import Fernet
import sys
import os
import json
import hashlib
import base64
import shutil
import time
import sqlite3
import shlex
import argparse
import subprocess
import random

#set default encoding to UTF-8
#might want to use 'export PYTHONIOENCODING=UTF8' in shell
reload(sys)
sys.setdefaultencoding('UTF-8')

#global variables
pythonV2 = sys.version_info[0] == 2
passwordFile=None
passwordFileBackups=10
homeDir = expanduser("~")
key=None
database = None
databaseCursor = None
usePwgenPasswords=False
pwgenDefaultLength=10
pwgenOpts="-cn1s"

PROGRAMNAME="CLI Password Manager"
VERSION="0.3"
COPYRIGHT="Copyright (C) 2015 by Sami Salkosuo."
LICENSE="Licensed under the Apache License v2.0."

CONFIG_FILE=".clipwdmgrcfg"
PROMPTSTRING="pwdmgr>"
DEFAULT_FILE_NAME="clipwds"
DEBUG=False
ERROR_FILE="%s/clipwdmgr_error.log" % homeDir
DEBUG_FILE="%s/clipwdmgr_debug.log" % homeDir

#JSON keys
JSON_META='meta'
JSON_ACCOUNTS='accounts'
#metakeys
JSONMETAKEY_CREATED='created'
JSONMETAKEY_UPDATED='updated'
JSONMETAKEY_SEQ='seq'
JSONMETAKEY_TOTALACCOUNTS='total.accounts'
JSONMETAKEY_COPYTOCLIPBOARD='copy.password.to.clipboard'
JSONMETAKEY_PWDMASKINLIST='pwd.mask.in.list'
JSONMETAKEY_PASSWORDFILEBACKUPS='password.file.backups'
JSONMETAKEY_PWGENENABLED='pwgen.enabled'
JSONMETAKEY_PWGENDEFAULTLENGTH='pwgen.default.length'
JSONMETAKEY_PWGENOPTS='pwgen.opts'
#account keys
JSONKEY_ID="ID"
JSONKEY_CREATED="CREATED"
JSONKEY_UPDATED="UPDATED"
JSONKEY_NAME="NAME"
JSONKEY_COMMENT="COMMENT"
JSONKEY_USERNAME="USERNAME"
JSONKEY_EMAIL="EMAIL"
JSONKEY_PWD="PASSWORD"
JSONKEY_LIST=[JSONKEY_ID,JSONKEY_CREATED,JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_COMMENT,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD]

#command line args
args=None

def parseCommandLineArgs():
	#parse command line args
	parser = argparse.ArgumentParser(description='Command Line Password Manager.')
	parser.add_argument('-c','--cmd', nargs='*', help='Execute command(s) and exit.')
	parser.add_argument('-f','--file', nargs=1, help='Password file.')
	parser.add_argument('-n','--new', action='store_true', help='Create new password file if -f file does not exist.')
	parser.add_argument('--debug', action='store_true', help='Show debug info.')
	parser.add_argument('--version', action='version', version="%s v%s" % (PROGRAMNAME, VERSION))
	global args
	global DEBUG
	args = parser.parse_args()
	DEBUG=args.debug

def main():
	print "%s v%s" % (PROGRAMNAME, VERSION)
	print
	if DEBUG:
		print "DEBUG is True"
	
	debug("command line args: %s" % args)

	config()

	if args.cmd is not None:
		#execute given commands
		cmds=args.cmd
		debug("commands: %s" % cmds)
		for cmd in cmds:		
			openDatabase()
			try:
				debug("Calling %s..." % cmd)
				callCmd(cmd)
			except:
				error()
			closeDatabase()
		return

	#shell
	userInput=prompt(PROMPTSTRING)
	while userInput!="exit":
		openDatabase()
		try:
			callCmd(userInput)
		except:
			error()
		closeDatabase()
		userInput=prompt(PROMPTSTRING)

def callCmd(userInput):
	inputList=shlex.split(userInput)
	if len(inputList)==0:
		return
	if inputList[0].lower()=="select":
		inputList=userInput.split(" ")
	debug("User input: [%s]" %  ','.join(inputList))
	debug("User input len: [%d]" %  len(inputList))
	cmd=inputList[0].lower()
	functionName = "%sCommand" % cmd
	debug("Function name: %s" % functionName)
	#call command
	function = globals().get(functionName)
	if not function:
  		print "%s not implemented." % cmd
  	else:
		function(inputList)

#================IMPLEMENTED COMMANDS===============
#to add new commands use function name
#<CMD<Command where CMD is input from user.
#Include docstring in function using format:
#    [args]||description
#if no args use: "||description"
#see examples below

def addCommand(inputList):
	"""
	||Add new account.
	"""
	debug("entering addCommand")
	pwdJSON=loadAccounts()
	#interactove to ask 
	name=prompt ("Name     : ")
	while name == "":
		print "Empty name not accepted"
		name=prompt ("Name     : ")
	uid=prompt ("User name: ")
	email=prompt("Email    : ")
	pwd=getPassword()
	comment=prompt ("Comment  : ")
	id=currentTimeMillis()
	timestamp=currentTimestamp()

	databaseCursor.execute("INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?)",
				(id,
				timestamp,
				timestamp,
				name,
				comment,
				uid,
				email,
				pwd)
				)
	
	saveAccounts(pwdJSON)

def listCommand(inputList):
	"""
	[<start of name> | json]||Print all or given accounts. If json is given, print JSON.
	"""
	debug("entering listCommand")
	pwdJSON=loadAccounts()
	if(len(inputList)>1 and inputList[1]=="json"):
		prettyJSON= json.dumps(pwdJSON, sort_keys=True,
							indent=2, separators=(',', ': '))
		print prettyJSON
		return

	maskPassword=boolValue(pwdJSON[JSON_META][JSONMETAKEY_PWDMASKINLIST])
	
	columnLength=maxColumnLength()
	#align="<"
	formatString=getColumnFormatString(5,columnLength)
	headerLine=formatString.format(JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT)

	where=""
	if(len(inputList)==2):
		where="where name like \"%s%%\"" % inputList[1]
	sql="select %s,%s,%s,%s,%s from accounts %s order by %s" % (JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT,where,JSONKEY_NAME)
	debug("SQL: %s" % sql)
	print headerLine
	for row in databaseCursor.execute(sql):
		account=dict()
		account[JSONKEY_NAME]=row[JSONKEY_NAME]
		account[JSONKEY_USERNAME]=row[JSONKEY_USERNAME]
		account[JSONKEY_EMAIL]=row[JSONKEY_EMAIL]
		pwd=row[JSONKEY_PWD]
		if maskPassword:
			pwd="********"			
		account[JSONKEY_PWD]=pwd
		account[JSONKEY_COMMENT]=row[JSONKEY_COMMENT]
		print accountLine(account,columnLength,formatString)

def viewCommand(inputList):
	"""
	<start of name>||View account(s) details.
	"""
	debug("entering viewCommand")
	if verifyArgs(inputList,2)==False:
		return

	arg=inputList[1]
	jsonObj=loadAccounts()
	meta=jsonObj[JSON_META]
	copyPassword=boolValue(meta[JSONMETAKEY_COPYTOCLIPBOARD])
	
	where="where name like \"%s%%\"" % arg
	sql="select %s,%s,%s,%s,%s,%s,%s,%s from accounts %s order by %s" % (JSONKEY_ID,JSONKEY_CREATED, JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT,where,JSONKEY_NAME)
	debug("SQL: %s" % sql)
	formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
	for row in databaseCursor.execute(sql):
		printAccountRow(row)
		pwd=row[JSONKEY_PWD]
		if copyPassword==True:
			print
			copyToClipboard(pwd)
			print "Password copied to clipboard."

def metaCommand(inputList):
	"""
	||View meta data.
	"""
	debug("entering viewCommand")
	jsonObj=loadAccounts()
	meta=jsonObj[JSON_META]
	#print metadata
	lens=[]
	keys=[]
	for key in meta:
		lens.append(len(key))
		keys.append(key)
	maxlen=max(lens)
	keys.sort()
	formatString=getColumnFormatString(2,maxlen,delimiter=" ",align="<")
	for key in keys:
		value=meta[key]
		if key==JSONMETAKEY_UPDATED or key==JSONMETAKEY_CREATED:
			value=formatTimestamp(value)
		print formatString.format(key,value)

def	metasetCommand(inputList):
	"""
	<key> <value>||Set key:value to JSON meta data.
	"""
	debug("entering metasetCommand")
	if verifyArgs(inputList,3)==False:
		return
	key=inputList[1]
	if key in [JSONMETAKEY_SEQ,JSONMETAKEY_CREATED,JSONKEY_UPDATED,JSONMETAKEY_TOTALACCOUNTS]:
		print "Can not set '%s'." % key
		return
	value=inputList[2]
	jsonObj=loadAccounts()
	meta=jsonObj[JSON_META]
	meta[key]=value
	loadMetaConfig(jsonObj)
	saveAccounts(jsonObj)
	print "%s is set to %s." % (key,value)

def selectCommand(inputList):
	"""
	<rest of select SQL>||Execute SELECT SQL.
	"""
	debug("entering selectCommand")
	loadAccounts()
	sql="SELECT %s" % " ".join(inputList[1:])
	debug("Executing: %s" % sql)

	databaseCursor.execute(sql)
	columnNames=getColumnNames(databaseCursor.description)
	print ",".join(columnNames)
	formatOutput=False
	if formatOutput==False:
		for row in databaseCursor:
			print row	
	else:
		rows=[]
		maxlen=0
		for row in databaseCursor:
			rowList=[]
			for column in columnNames:
				v=row[column]
				vlen=len(v)
				if vlen>maxlen:
					maxlen=vlen
				rowList.append(v)
			rows.append(rowList)

		formatString=getColumnFormatString(len(columnNames),maxlen)
		headerLine=formatString.format(*columnNames)
		print headerLine
		for row in rows:
			print formatString.format(*row)
	#print "|".join(columnNames)

def exportjsonCommand(inputList):
	"""
	<filename>||Export accounts as JSON to a file.
	"""
	debug("entering exportJSONCommand")
	if verifyArgs(inputList,2)==False:
		return
	filename=inputList[1]
	debug("JSON Filename: %s" % filename)
	pwdJSON=loadAccounts()
	jsonString=json.dumps(pwdJSON[JSON_ACCOUNTS], sort_keys=True,
						indent=2, separators=(',', ': '))
	createNewFile(filename,[jsonString])
	print "Accounts exported to %s." % filename

def loadjsonCommand(inputList):
	"""
	<filename>||Load accounts from file. Overrides any existing accounts.
	"""
	debug("entering loadJSONCommand")
	if verifyArgs(inputList,2)==False:
		return
	filename=inputList[1]
	jsonString=readFileAsString(filename)
	accounts=json.loads(jsonString)
	databaseCursor.execute("delete from accounts")
	populateAccountsTable(accounts)
	saveAccounts(loadJSONFile())
	print "Accounts imported."


def changepassphraseCommand(inputList):
	"""
	||Change passphrase.
	"""
	debug("entering changepassphraseCommand")
	#change encryption key
	newKey=askKey("New passphrase: ")
	if newKey==None:
		return
	newKey2=askKey("Passphrase again: ")
	if newKey!=newKey2:
		print "Passphrases do not match."
		return

	pwdJSON=loadAccounts()
	global key
	key=newkey
	saveAccounts(pwdJSON)
	print "Key changed."

def deleteCommand(inputList):
	"""
	<start of name>||Delete account(s) that match given string.
	"""
	debug("entering deleteCommand")
	if verifyArgs(inputList,2)==False:
		return
	pwdJSON=loadAccounts()
	arg=inputList[1]
	where="where name like \"%s%%\"" % arg
	sql="select %s,%s,%s,%s,%s,%s,%s,%s from accounts %s order by %s" % (JSONKEY_ID,JSONKEY_CREATED, JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT,where,JSONKEY_NAME)
	debug("SQL: %s" % sql)
	formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
	deletedSomething=False
	for row in databaseCursor.execute(sql):
		printAccountRow(row)
		id=str(row[JSONKEY_ID])
		if boolValue(prompt("Delete this account (yes/no)? ")):			
			sql="delete from accounts where %s=%s" % (JSONKEY_ID,id)
			delCursor=database.cursor()	
			delCursor.execute(sql)
			deletedSomething=True
			print "Account deleted."
	if deletedSomething:
		saveAccounts(pwdJSON)

def searchCommand(inputList):
	"""
	<string in name or comment> | username=<string> | email=<string>||Search accounts that have matching string.
	"""
	debug("entering searchCommand")
	if verifyArgs(inputList,2)==False:
		return
	pwdJSON=loadAccounts()
	arg=inputList[1]
	where=""
	if arg.startswith("username="):
		arg=arg.replace("username=","")
		where="where %s like '%%%s%%' " % (JSONKEY_USERNAME,arg)
	elif arg.startswith("email="):
		arg=arg.replace("email=","")
		where="where %s like '%%%s%%' " % (JSONKEY_EMAIL,arg)
	else:
		where="where %s like '%%%s%%' or %s like '%%%s%%' " % (JSONKEY_NAME,arg,JSONKEY_COMMENT,arg)
	sql="select %s,%s,%s,%s,%s,%s,%s,%s from accounts %s order by %s" % (JSONKEY_ID,JSONKEY_CREATED, JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT,where,JSONKEY_NAME)
	for row in databaseCursor.execute(sql):
		printAccountRow(row)

def modifyCommand(inputList):
	"""
	<start of name>||Modify account(s).
	"""
	debug("entering modifyCommand")
	if verifyArgs(inputList,2)==False:
		return
	pwdJSON=loadAccounts()
	arg=inputList[1]
	where="where name like \"%s%%\"" % arg
	sql="select %s,%s,%s,%s,%s,%s,%s,%s from accounts %s order by %s" % (JSONKEY_ID,JSONKEY_CREATED, JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT,where,JSONKEY_NAME)
	debug("SQL: %s" % sql)
	formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
	accountUpdated=False
	for row in databaseCursor.execute(sql):
		printAccountRow(row)
		name=row[JSONKEY_NAME]
		id=str(row[JSONKEY_ID])
		username=row[JSONKEY_USERNAME]
		email=row[JSONKEY_EMAIL]
		pwd=row[JSONKEY_PWD]
		comment=row[JSONKEY_COMMENT]
		if boolValue(prompt("Modify this account (yes/no)? ")):
			name=modPrompt("Name",name)
			username=modPrompt("User name",username)
			email=modPrompt("Email",email)
			if usePwgenPasswords and pwgenAvailable():
				print "pwgen is available. Type your password or type 'p' to generate password."
			pwd=modPrompt("Password",pwd)
			if pwd=="p":
			 	pwd=getPassword()

			comment=modPrompt("Comment",comment)
			updated=currentTimestamp()
			sql="update accounts set %s='%s',%s='%s',%s='%s',%s='%s',%s='%s',%s=%s where id=%s" % (
				JSONKEY_NAME,name,
				JSONKEY_USERNAME,username,
				JSONKEY_EMAIL,email,
				JSONKEY_PWD,pwd,
				JSONKEY_COMMENT,comment,
				JSONKEY_UPDATED,updated,
				id)
			updateCursor=database.cursor()	
			updateCursor.execute(sql)
			accountUpdated=True
			print "Account updated."
	if accountUpdated==True:
		saveAccounts(pwdJSON)

def exitCommand(inputList):
	"""||Exit program."""
	pass

def pwdCommand(inputList):
	"""
	[<number of pwds>] [<pwd length>]||Generate password(s).
	"""
	debug("entering pwdCommand")
	if pwgenAvailable()==True:
		inputLen=len(inputList)
		N=1
		pwdLen=pwgenDefaultLength
		
		if inputLen==2:
			#number specified
			N=int(inputList[1])
		if inputLen==3:
			#length and number of pwd specified
			N=int(inputList[1])
			pwdLen=int(inputList[2])
		
		pwds=pwgenPassword(length=pwdLen,n=N)
		if N==1:
			print pwds
		else:
			for pwd in pwds:
				print pwd
	else:
		print "pwgen is not available. No passwords generated."

def helpCommand(inputList):
	"""||This help."""
	debug("entering helpCommand")
	versionInfo()
	print 
	print "Commands:"
	names=globals().keys()
	names.sort()
	maxLenName=0
	maxLenArgs=0
	maxLenDesc=0
	commandList=[]
	for name in names:
		if name.endswith("Command"):
			cmdName=name.replace("Command","").lower()
			func=globals().get(name)
			(args,desc)=getDocString(func)
			if len(cmdName)>maxLenName:
				maxLenName=len(cmdName)
			if len(args)>maxLenArgs:
				maxLenArgs=len(args)
			if len(desc)>maxLenDesc:
				maxLenDesc=len(desc)
			commandHelp=[cmdName,args,desc]
			commandList.append(commandHelp)
	formatStringName=getColumnFormatString(1,maxLenName,delimiter=" ",align="<")
	formatStringArgs=getColumnFormatString(1,maxLenArgs,delimiter=" ",align="<")
	formatStringDesc=getColumnFormatString(1,maxLenDesc,delimiter=" ",align="<")

	for c in commandList:
		print "  ",formatStringName.format(c[0]),formatStringArgs.format(c[1]),formatStringDesc.format(c[2])

def	debugCommand(inputList):
	"""
	on|off||Print or don't print debug info.
	"""
	debug("entering debugCommand")
	if verifyArgs(inputList,2)==False:
		return
	global DEBUG
	DEBUG=boolValue(inputList[1])
	print "DEBUG is",DEBUG

#================END IMPLEMENTED COMMANDS===============

def openDatabase():
	global database
	global databaseCursor
	database=sqlite3.connect(':memory:')
	database.row_factory = sqlite3.Row
	databaseCursor=database.cursor()	
	databaseCursor.execute('''CREATE TABLE accounts
            (%s INTEGER, %s INTEGER, %s INTEGER, %s TEXT, %s TEXT, %s TEXT, %s TEXT, %s TEXT)''' % 
            (JSONKEY_ID,JSONKEY_CREATED,JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_COMMENT,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD))

def closeDatabase():
	global database
	global databaseCursor
	if database is not None:
		database.close()
	database=None
	databaseCursor=None

def getDocString(commandFunc):
	#return tuple from command function
	docString=commandFunc.__doc__
	args=""
	desc=""
	debug("Parsing %s" % commandFunc)
	if docString is not None:
		try:
			docString=docString.strip()
			doc=docString.split("||")
			args=doc[0].strip()
			desc=doc[1].strip()
		except:
			desc=docString
	else:
		desc="Not documented."
	return (args,desc)

def getPassword():
	pwd=""
	if usePwgenPasswords and pwgenAvailable():
		print "Password generated using pwgen. Type your password or type 'p' to generate new password."
		pwd=pwgenPassword()
		pwd2=prompt("Password (%s): " % pwd)
		debug("pwd2: %s (%d)" % (pwd2,len(pwd2)))
		while pwd2.lower()=="p":
			pwd=pwgenPassword()
			pwd2=prompt("Password (%s): " % pwd)
		if pwd2!="":
			pwd=pwd2
	else:
		pwd=prompt("Password : ")

	return pwd

def verifyArgs(inputList,numberOfArgs):
	ilen=len(inputList)
	debug("len(inputList): %d" % ilen)
	if ilen != numberOfArgs:
		cmdName=inputList[0].lower()
		cmd="%sCommand" % cmdName
		func=globals().get(cmd)
		(args,desc)=getDocString(func)
		print "Wrong number of arguments."
		print "Usage: %s %s" % (cmdName, args)
		return False
	return True

def pwgenAvailable():
	try:
		subprocess.check_output(["pwgen"])
		return True
	except:
		print "pwgen is not available."
		return False

def pwgenPassword(length=None,n=None):
	pwd=None
	if length==None:
		length=pwgenDefaultLength

	nornd=False
	N=10
	if n==None or n==1:
		N=10
	else:
		N=n
		nornd=True

	if pwgenAvailable():
		opts=pwgenOpts#"-cn1s"#"-cnB1s"
		pwd=subprocess.check_output(["pwgen", opts,str(length),str(N)])
		pwd=pwd.split()
		debug("passwords: %s" % pwd)
		if nornd==False:
			l=len(pwd)
			pwd=pwd[random.randint(0, l-1)]
		
	return pwd

def versionInfo():
	print "%s v%s" % (PROGRAMNAME, VERSION)
	print COPYRIGHT
	print LICENSE


def modPrompt(field,defaultValue):
	n=prompt("%s (%s): " % (field,defaultValue))
	if n=="":
		n=defaultValue
	return n

def printAccountRow(row):
	formatString=getColumnFormatString(2,10,delimiter=" ",align="<")
	name=row[JSONKEY_NAME]
	print "==============================="# % (name)
	print formatString.format(JSONKEY_NAME,name)
	#print "========== %s ==========" % name
	id=str(row[JSONKEY_ID])
	print formatString.format(JSONKEY_ID,id)
	username=row[JSONKEY_USERNAME]
	print formatString.format(JSONKEY_USERNAME,username)
	email=row[JSONKEY_EMAIL]
	print formatString.format(JSONKEY_EMAIL,email)
	pwd=row[JSONKEY_PWD]
	print formatString.format(JSONKEY_PWD,pwd)
	timestamp = formatTimestamp(row[JSONKEY_CREATED])
	print formatString.format(JSONKEY_CREATED,timestamp)
	timestamp = formatTimestamp(row[JSONKEY_UPDATED])
	print formatString.format(JSONKEY_UPDATED,timestamp)
	comment=row[JSONKEY_COMMENT]
	print formatString.format(JSONKEY_COMMENT,comment)

def accountLine(account,maxColumnLength,formatString):
	desc=account[JSONKEY_COMMENT]
	if len(desc)>maxColumnLength:
		desc="%s..." % desc[0:maxColumnLength-3]
	line=formatString.format(account[JSONKEY_NAME],account[JSONKEY_USERNAME],account[JSONKEY_EMAIL],account[JSONKEY_PWD],desc)
	return line
	
def config():
	global passwordFile
	if args.file==None:
		##read congig file and create it if not exists
		configFile="%s/%s" % (homeDir,CONFIG_FILE)
		if os.path.isfile(configFile) == False:
			print "Config file %s does not exist." % CONFIG_FILE
			print "Creating new one..."
			dir=prompt("Password file directory (~): ")
			if dir=="":
				dir=homeDir
			filename=prompt("Password file name (%s): " % DEFAULT_FILE_NAME)
			if filename=="":
				filename=DEFAULT_FILE_NAME
			createNewFile(configFile,["[config]",
				"password.file.dir=%s" % dir,
				"password.file.name=%s" % filename
			])
			print "Config file saved as %s" % configFile
		else:
			printConfig=False
			if printConfig:
				print "Current configuration %s" % configFile
				file=open(configFile,"r")
				for line in file:
					print line
				file.close()
		#read config
		import ConfigParser
		configParser = ConfigParser.RawConfigParser()   
	 	configParser.read(r'%s' % configFile)
		passwordDir=configParser.get('config', 'password.file.dir')
		passwordFileName=configParser.get('config', 'password.file.name')

		#add version to default file name
		passwordFileName="%s-%s.txt" % (passwordFileName,VERSION)
		passwordFile="%s/%s" % (passwordDir,passwordFileName)
	else:
		passwordFile=args.file[0]
		if os.path.isfile(passwordFile) == False and args.new==None:
			raise RuntimeError("Password file %s does not exist." % passwordFile)

	debug("Password file: %s." % (passwordFile))
	#read passphrase/key
	global key
	key=askKey("Passphrase (CTRL-C to quit): ")
	if key==None:
		raise RuntimeError("Empty key not supported.")
	#check passwords file
	if os.path.isfile(passwordFile) == False:
		print "File %s does not exist. Creating one..." % passwordFile
		key2=askKey("Passphrase again: ")
		if key!=key2:
			raise RuntimeError("Passphrases do not match.")

		ctime=currentTimestamp()
		#JSON meta includes configuration settingss
		emptyJSON={JSON_META:{
				JSONMETAKEY_CREATED:ctime,
				JSONMETAKEY_UPDATED:ctime,
				JSONMETAKEY_SEQ:0,
				JSONMETAKEY_TOTALACCOUNTS:0,
				JSONMETAKEY_COPYTOCLIPBOARD:True,
				JSONMETAKEY_PWDMASKINLIST:True,
				JSONMETAKEY_PASSWORDFILEBACKUPS:10,
				JSONMETAKEY_PWGENENABLED:True,
				JSONMETAKEY_PWGENDEFAULTLENGTH:12,
				JSONMETAKEY_PWGENOPTS:"-cn1sy"
				},
		        JSON_ACCOUNTS:[]
		        }
		debug(emptyJSON)
		openDatabase()
		saveAccounts(emptyJSON)
		closeDatabase()
	#set congig from json meta
	loadMetaConfig()

def loadMetaConfig(jsonObj=None):
	global usePwgenPasswords
	global pwgenDefaultLength
	global pwgenOpts
	if jsonObj==None:
		fernet = Fernet(key)
		encryptedJSON=readFileAsString(passwordFile)
		jsonString=fernet.decrypt(encryptedJSON)
		jsonObj=json.loads(jsonString)
	
	meta=jsonObj[JSON_META]
	usePwgenPasswords=boolValue(meta[JSONMETAKEY_PWGENENABLED])
	pwgenDefaultLength=int(meta[JSONMETAKEY_PWGENDEFAULTLENGTH])
	pwgenOpts=meta[JSONMETAKEY_PWGENOPTS]

def loadAccounts():
	jsonObj=loadJSONFile()
	loadMetaConfig(jsonObj)
	accounts=jsonObj[JSON_ACCOUNTS]
	populateAccountsTable(accounts)
	return jsonObj

def loadJSONFile():
	fernet = Fernet(key)
	encryptedJSON=readFileAsString(passwordFile)
	jsonString=fernet.decrypt(encryptedJSON)
	jsonObj=json.loads(jsonString)
	return jsonObj

def populateAccountsTable(accounts):
	#insert all accounts to in-memory sqlite
	for account in accounts:
		databaseCursor.execute("INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?)",
				(account[JSONKEY_ID],
				account[JSONKEY_CREATED],
				account[JSONKEY_UPDATED],
				account[JSONKEY_NAME],
				account[JSONKEY_COMMENT],
				account[JSONKEY_USERNAME],
				account[JSONKEY_EMAIL],
				account[JSONKEY_PWD])
				)

def saveAccounts(contentJSON):
	#modify metadata
	meta=contentJSON[JSON_META]
	meta[JSONMETAKEY_UPDATED]=currentTimestamp()
	seq=meta[JSONMETAKEY_SEQ]
	meta[JSONMETAKEY_SEQ]=seq+1
	passwordsFilesToKeep=int(meta[JSONMETAKEY_PASSWORDFILEBACKUPS])
	#meta is kept
	#accounts from inmemory sqlite
	sql="select %s,%s,%s,%s,%s,%s,%s,%s from accounts order by %s" % (JSONKEY_ID,JSONKEY_CREATED, JSONKEY_UPDATED,JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD,JSONKEY_COMMENT,JSONKEY_NAME)
	debug("SQL: %s" % sql)
	accounts=[]
	for row in databaseCursor.execute(sql):
		id=row[JSONKEY_ID]
		name=row[JSONKEY_NAME]
		username=row[JSONKEY_USERNAME]
		email=row[JSONKEY_EMAIL]
		pwd=row[JSONKEY_PWD]
		created = row[JSONKEY_CREATED]
		updated=row[JSONKEY_UPDATED]
		comment=row[JSONKEY_COMMENT]

		accounts.append({JSONKEY_ID:id,
			JSONKEY_CREATED:created,
			JSONKEY_UPDATED:updated,
			JSONKEY_NAME:name,
			JSONKEY_USERNAME:username,
			JSONKEY_EMAIL:email,
			JSONKEY_PWD:pwd,
			JSONKEY_COMMENT:comment
			})
	
	contentJSON[JSON_ACCOUNTS]=accounts
	meta[JSONMETAKEY_TOTALACCOUNTS]=len(accounts)
	jsonString=json.dumps(contentJSON)

	debug("JSON: %s" % jsonString)
	fernet = Fernet(key)
	encryptedJSON = fernet.encrypt(jsonString)
	createFileBackups(passwordFile,passwordsFilesToKeep)
	createNewFile(passwordFile,[encryptedJSON])

def createNewFile(filename, lines=[]):
	fileExisted=os.path.isfile(filename)
	file=open(filename,"w")
	file.write("\n".join(lines))
	file.close()
	if fileExisted:
		debug("File overwritten: %s" % filename)
	else:
		debug("Created new file: %s" % filename)

def appendToFile(filename, lines=[]):
	file=open(filename,"a")
	file.write("\n".join(lines))
	file.close()

def readFileAsString(filename):
	file=open(filename,"r")
	lines=[]
	for line in file:
		lines.append(line)
	file.close()
	return "".join(lines)

def createFileBackups(filename,maxBackups):
	if os.path.isfile(filename)==False:
		return
	currentBackup=maxBackups
	while currentBackup>0:
		backupFile="%s.%d" % (passwordFile, currentBackup)
		if os.path.isfile(backupFile) == True:
			shutil.copy2(backupFile, '%s.%d' % (passwordFile,currentBackup+1))
		debug("Backup file: %s" % backupFile)
		currentBackup=currentBackup-1
	shutil.copy2(passwordFile, '%s.1' % passwordFile)

def toHexString(byteStr):
    return ''.join(["%02X" % ord(x) for x in byteStr]).strip()

def prompt(str):
	if pythonV2:
		inputStr = raw_input(str)
	else:
  		inputStr = input(str)
  	inputStr=unicode(inputStr,"UTF-8")
  	return inputStr

def askKey(str):
	import getpass
	passphrase=getpass.getpass(str)
	if passphrase=="":
		return None
	passphrase=hashlib.sha256(passphrase).digest()
	key=base64.urlsafe_b64encode(passphrase)
	return key


def debug(str):
	if DEBUG:
		msg="%s: %s" % (datetime.now(),str)
		if DEBUG_FILE is not None:
			file=open(DEBUG_FILE,"a")
			file.write("%s\n" % msg)
			file.close()
		print msg

def error():
	import traceback
	str=traceback.format_exc()
	print str
	msg="%s: %s" % (datetime.now(),str)
	appendToFile(ERROR_FILE,[msg])

def currentTimeMillis():
	return int(round(time.time() * 1000))

def currentTimestamp():
	return time.time()

def formatTimestamp(timestamp):
	return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def boolValue(value):
	string=str(value)
  	return string.lower() in ("yes","y","true", "on", "t", "1")

def getColumnNames(description):
	#get column names from sqlite description
	names=[]
	for desc in description:
		names.append(desc[0])
	return names

def maxColumnLength():
	#longest value from name, username, pwd and email sqlite columns
	maxes=[0]
	for row in databaseCursor.execute("select max(length(%s),length(%s),length(%s),length(%s)) from accounts" % (JSONKEY_NAME,JSONKEY_USERNAME,JSONKEY_EMAIL,JSONKEY_PWD)):
		maxes.append(row[0])
	maxColumnLength=max(maxes)
	debug("Max column length: %d" % maxColumnLength)
	return maxColumnLength

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

def copyToClipboard(str):
	import pyperclip
	pyperclip.copy(str)

if __name__ == "__main__": 
	parseCommandLineArgs()
	debug("START")
	try:
		main()
	except:
		error()
	debug("END")
