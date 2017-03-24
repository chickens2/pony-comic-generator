# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :


"""
Takes an input folder and generates a comic on a random line selection from a random file from within the folder
"""

import pyperclip
import io
import sys
import os
import configparser
import utilFunctions
import string
import random
from generateComic import processChatLog
from lime2input import convertLimelog

"""
Command-line options:

-i input folder for "normal"-format logs
-m input folder for logs stored in the LimeChat format
-l force a specific length of dialogue
-s set the intial seed
-b use the seed for the seed in as many places as possible

Either -i or -m is required; behavior is not defined if you use both
"""

# handle the command line options
nextToFill= None # iterator
inputfolder = None # input log folder
outputLog = None # converted log folder
needlime = False # need limechat conversion
bigseed = None
forceseed = False
forcelines = None
for arg in sys.argv:
	if arg[0] == '-':
		nextToFill = arg[1:].lower()
	else:
		if nextToFill is not None:
			if nextToFill[0] == 'i':
				inputfolder = arg
			if nextToFill[0] == 'm':
				inputfolder = arg
				needlime = True
			if nextToFill[0] == 'l':
				forcelines = int(arg)
			if nextToFill[0] == 's':
				bigseed = arg
			if nextToFill[0] == 'b':
				bigseed = arg
				forceseed = True
		nextToFill = None
if inputfolder is None:
	print("Need to know where the chatlogs are")
	sys.exit(1)
if bigseed is not None:
	random.seed(bigseed)
if forcelines is not None and forcelines < 1:
	forcelines = None


config = configparser.ConfigParser(inline_comment_prefixes=(';',))
config.readfp(open('config.cfg'))

badfiles = config.get('Ignore','banned_backgrounds').split()
skipname = config.get('Ignore','ignored_nicks').split()
removebot = config.get('Options','remove_bot_commands').upper()=='TRUE'


# pick the number of lines of use
def picklines(seed=None):
	if seed is not None:
		random.seed(seed)
	lines =  int(random.gauss(6.022,4.54))
	if lines > 0:
		return lines
	return lines%3+1

# Pick a line
def getcontent(logspot, needlime = False):
	content = open(logspot).readlines()
	if needlime:
		content = convertLimelog(content, 46)
	return content



"""
Actual program here

1. Pick number of lines
2. Open a file
3. Grab lines until you have enough valid ones, going to the next file if necessary
4. Run lines through processChatlog
"""

# Pick the number of lines
seed = None
if forceseed is True:
	seed = bigseed
if forcelines is None:
	length = picklines(seed)
else:
	length = forcelines
print(("Choosing "+str(length)+" lines"))

# Pick a file
inputfolder, filelist, logloc = utilFunctions.pickfileIndex(inputfolder, badfiles)
print(("Starting at index "+str(logloc)+" of "+str(filelist)+" from "+inputfolder))
if needlime is True:
	print("TAKING A MOMENT TO CONVERT")

content = getcontent(inputfolder+'/'+filelist[logloc], needlime)
start = random.randint(0, len(content)-1)
print(("Starting at line #"+str(start)))

# Run with it
selectedlines = []
while length > 0:
	line = content[start]
	if (utilFunctions.quitline(line) is False and
			line is not None and
			line != '\n' and
			len(line) > 1 and
			utilFunctions.cleanupline(line, [], ignored_users=skipname, params={'bot':removebot,'debug':False}) is not None and
			utilFunctions.soloURL(' '.join(line.split(' ')[1:])) is False):
		selectedlines.append(line)
		length -= 1
	start += 1
	# move to the next log if you're at the end
	if start == len(content):
		start = 0
		found = False
		print("Found end of file, trying for the next log")
		while found is False:
			logloc += 1
			# if you've reached the end of the folder, stop processing files
			if logloc == len(filelist):
				length = 0
				print("Reached end of directory: stopping here")
				break
			# skip the junk files
			nextfile = filelist[logloc]
			if nextfile in badfiles:
				print(("Skipping junk file "+nextfile))
				continue
			# skip any directories
			if os.path.isdir(os.path.join(inputfolder, nextfile)) is True:
				print(("Skipping directory "+nextfile))
				continue
			content = getcontent(inputfolder+'/'+filelist[logloc], needlime)
			print(("Continuing with "+nextfile))
			found = True



print(selectedlines)

processChatLog(selectedlines)


#from lime2input import convertLimeLog
