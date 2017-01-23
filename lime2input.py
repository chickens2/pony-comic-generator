# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import pyperclip
import StringIO
import sys
import os
import utilFunctions
import string

"""
Converts LimeChat-formatted logs into the expected format for the comic parses
Makes intelligent guesses at what should become a /me statement, since those aren't stored by LimeChat
If input/output filenames aren't specified, the clipboard will suffice for the missing filename
Expected format is "hh:mm username: message" for input files

guessMode (set with -A command) options:
0: only turn lines without a colon after the username into a /me command (useful for copying from clipboard)
1: run all lines through the /me guesser
2: ignore the case sensitivity of the /me guesser
"""

# command line options
nextToFill= None # iterator
limeLog = None # input log
outputLog = None # converted log
guessMode = 0
for arg in sys.argv:
	if arg[0] == '-':
		nextToFill = arg[1:].lower()
	else:
		if nextToFill is not None:
			if nextToFill[0] == 'i':
				limeLog = arg
			if nextToFill[0] == 'o':
				outputLog = arg
			if nextToFill[0] == 'A':
				guessMode = int(arg)

#
def convertLimelog(limechat, gm):
	newchat = []
	rawwords = []
	for line in limechat:
		rawwords.append(line.split())
		# rawwords should be an array of arrays, with the inner array being ["hh:mm", "nick", "word1", "word2", etc…]
	for wordlist in rawwords:
		newchat.append(processLine(wordlist[1],wordlist[2:],gm))
		newchat += '\n'
	return newchat

"""
name: nick saying the line
message: array of strings, each containing a word in the message
guessstrat: how aggressive to be when guessing at what is a /me statement
"""
def processLine(name, message, guessstrat):
	newline = ""
	if ':' not in name: # explicit /me command
		return assembleMeLine(name, message)


	return assembleNormalLine(name, message)

#
def assembleMeLine(name, messagewords):
	return "* " + name + " " + " ".join(messagewords)

#
def assembleNormalLine(name, messagewords):
	return "<" + name[:-1] + "> " + " ".join(messagewords)

chatfile = None
if limeLog is None:
	clipboard = pyperclip.paste().encode('utf8')
	chatfile = StringIO.StringIO(clipboard)
else:
	if '-A' not in sys.argv:
		guessMode == 1
	chatfile = open(limeLog).readlines()


newlog = convertLimelog(chatfile, guessMode)

if outputLog is None:
	pyperclip.copy("".join(newlog))
else:
	file = open(outputLog, 'w')
	file.writelines(newlog)
	file.close()
