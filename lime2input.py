# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import pyperclip
import io
import sys
import os
import utilFunctions
import string
import random

"""
Converts LimeChat-formatted logs into the expected format for the comic parses
Makes intelligent guesses at what should become a /me statement, since those aren't stored by LimeChat
If input/output filenames aren't specified, the clipboard will suffice for the missing filename
Expected format is "hh:mm username: message" for input files

USES PYTHON 3!!!!!!



guessstrat (set with -A command) options:
Add together one number from each group to determine the -A value you're after.

0: only turn lines without a colon after the username into a /me command, a.k.a. no guessing (useful for copying from clipboard, overrides all others)
1 (or 2, if you're a real joker): attempt to guess at lines that should be /me commands

0: do not check lines beginning with a capital letter (unless all caps)
3: check lines beginning with a capital line.  If found to be a /me command, make the 1st letter of the line lowercase
6: programatically decide whether or not to check lines beginning with a capital letter

0: do not check lines ending with a question mark
9: check lines ending with a question mark
18: programatically decide whether or not to check lines ending in a question mark

0: /me commands retain their original case
27: return an ALL CAPS /me message in lowercase
"""

# handle the command line options
nextToFill= None # iterator
limeLog = None # input log
outputLog = None # converted log
guessstrat = None
for arg in sys.argv:
	if arg[0] == '-':
		nextToFill = arg[1:].lower()
	else:
		if nextToFill is not None:
			if nextToFill[0] == 'i':
				limeLog = arg
				if guessstrat is None:
					guessstrat = 1
			if nextToFill[0] == 'o':
				outputLog = arg
			if nextToFill[0] == 'a':
				guessstrat = int(arg)
		nextToFill = None
if guessstrat is None:
	guessstrat = 0


# word lists
nonVerbSList = [
	"yours",
	"ours",
	"hours"
	"how's"
]
questionTriggerList = [
	"you",
	"they",
	"it",
	"we"
]
nonSVerbList = [ # also for words that often are part of a question
	"can't",
	"won't",
	"can",
	"will",
	"should",
	"should've",
	"could",
	"could've",
	"wants"
]
adverbCheckList = [
	"really",
	"really," # for when you really, really need to go
	"absolutely"
]
allowedPunctuation = [
	'!',
	'?',
	'.'
]



# Breaks a LimeChat log down into a name and a list of words, then sends them to the processor and returns the processed lines
def convertLimelog(limechat, guessstrat):
	newchat = []
	rawwords = []
	for line in limechat:
		rawwords.append(line.split())
		# rawwords should be an array of arrays, with the inner array being ["hh:mm", "nick", "word1", "word2", etc…]
	for wordlist in rawwords:
		if len(wordlist) > 3 and ':' in wordlist[2]: # remove time stamps from the bouncer
			wordlist.remove(wordlist[2])
		newchat.append(processLine(wordlist[1], wordlist[2:], guessstrat))
		newchat += '\n' # make sure everything is on its own line
	return newchat

"""
This function should be moved to a utils file or a text parsing backend module if another log converter is made

name: nick saying the line
message: array of strings, each containing a word in the message
guessstrat: see module header for details
"""
def processLine(name, message, guessstrat):
	#print "checking line " + str(message) + " with " + str(guessstrat)
	# handle errors
	if len(message) == 0:
		return ""
	# this if statement may need to be handled in convertLimeLog if this function is moved and the colon test is too specific to LimeChat
	if ':' not in name: # explicit /me command [nicks can't have a colon in them]
		return assembleMeLine(name, message)
	# Don't make any guesses if you didn't tell it to do so
	if guessstrat%3 == 0:
		return assembleNormalLine(name, message)
	# It's a /me line if the opening of the messages is 's
	if message[0] == "'s":
		return assembleMeLine(name,message)
	# if the line is just a comma or whatever, return it as a normal line
	if message[0].isalpha() is False and len(message) == 1:
		return assembleNormalLine(name, message)
	# if the line starts with a comma, it's probably a /me command
	if message[0] == "," or message[0] == ":":
		return assembleMeLine(name, message) # will probably want a backspace character as well so things render nicely, but that may break the parser
	# turn guessstrat into an actual workable list
	options = utilFunctions.decomposeNumericComponents(guessstrat,3)
	random.seed(str(message) + name)
	# optionally squish ALL CAPS messages
	ALLCAPS = wordlistIsUpper(message, True)
	if 27 in list(options.keys()) and ALLCAPS:
		message = lowerwordlist(message)

	# question test
	if message[-1][-1] == '?' and ( # if it's a question and…
		9 not in list(options.keys()) or ( # you didn't say you want it checked or…
			options[9] == 2 and utilFunctions.rollOdds(2) # you said to check it randomly
		)
	):
		return assembleNormalLine(name, message)

	if checkWordsForMe(message, options) is True:
		if ALLCAPS is False:
			message[0] = message[0].lower()
		return assembleMeLine(name[:-1], message)
	else:
		return assembleNormalLine(name, message)

# lowercases a list of words
def lowerwordlist(words):
	return [word.lower() for word in words]

# checks a list of words to determine whether it should be a /me statement
# treats an ALL CAPS message as all lower-case
def checkWordsForMe(words, options):
	#print "Checking words " + str(words) + " with options " + str(options)
	# check ALL CAPS message as if lower-case
	if wordlistIsUpper(words, False):
		return checkWordsForMe(lowerwordlist(words), options)
	if len(words) == 0:
		return utilFunctions.rollOdds(2) # if you pass an empty list of words, it's a 50/50 shot

	# deal with initial capital letter
	if words[0][0].isupper() and ( # if it starts with a capital letter and…
		3 not in list(options.keys()) or ( # you said not to bother with lines opening with capitals or…
			options[3] == 2 and utilFunctions.rollOdds(2) # you want capitalized lines to be checked randomly
		)
	):
		return False

	# this makes things easier later from here on
	word0 = words[0].lower()

	# clear out any opening adverb lists before processing the rest of the words
	if word0 in adverbCheckList:
		return checkWordsForMe(words[1:], options)
	# if the opening word is here, it's not a /me command
	if word0 in nonVerbSList:
		return False
	# if the opening word doesn't end in a letter, it's not a /me command
	if word0[-1].isalpha() is False and word0[-1] not in allowedPunctuation:
		return False
	# opening word ending with 's means it's totally not a sensible /me command
	if word0[-2:] == "'s":
		return False
	# if the 1st words doesn't end in s and isn't in the special list, it's probably not a /me command
	if word0[-1] != 's' and word0 not in nonSVerbList:
		return False
	# if it's in the special non-s list and the next word is one of these question triggers, it's not /me
	if word0 in nonSVerbList and len(words) > 1 and words[1].lower() in questionTriggerList:
		return False
	# if it hasn't triggered any of these conditions, it's probably /me
	return True

# checks if the entire wordlist is uppercase or non-alphabetic
def wordlistIsUpper(wordlist, countNA):
	for word in wordlist:
		if word.isupper() is False and (nonAlphaWord(word) is False or countNA is False):
			return False
	return True

# like isalpha, but checks that the entire word is non-alphabetic
def nonAlphaWord(word):
	for char in word:
		if char.isalpha():
			return False
	return True

'''
The following two functions should be moved to a utils file of text parsing module if another log converter is made
'''
# Takes a name and a list of words and creates a /me command for the parser to enjoy
def assembleMeLine(name, messagewords):
	return "* " + name + " " + " ".join(messagewords)

# Takes a name and a list of words and creates a normal line for the parser's enjoyment
# Assumes name has a colon appended after it
def assembleNormalLine(name, messagewords):
	return "<" + name[:-1] + "> " + " ".join(messagewords)



"""
Return to the imperative part of the program from here on
"""

def main():
	chatfile = None
	if limeLog is None:
		clipboard = pyperclip.paste().encode('utf8')
		chatfile = io.StringIO(clipboard)
	else:
		chatfile = open(limeLog).readlines()

	newlog = convertLimelog(chatfile, guessstrat)

	if outputLog is None:
		pyperclip.copy("".join(newlog))
	else:
		file = open(outputLog, 'w')
		file.writelines(newlog)
		file.close()

if __name__ == "__main__":
	main()