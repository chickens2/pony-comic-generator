# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :


"""
Takes an input folder and generates a comic on a random line selection from a random file from within the folder
"""

import pyperclip
import StringIO
import sys
import os
import utilFunctions
import string
import random
from makeComic import processChatLog
from lime2input import convertLimelog

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
	print "Need to know where the chatlogs are"
	sys.exit(1)
if bigseed is not None:
	random.seed(bigseed)
if forcelines < 1:
	forcelines = None




# pick the number of lines of use
def picklines(seed=None):
	if seed is not None:
		random.seed(seed)
	lines =  int(random.gauss(5,4))
	if lines > 0:
		return lines
	if lines%2 == 0:
		return 2;
	return 1;

def pickfile(inputfolder):
	return 0;




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
print "Choosing "+str(length)+" lines"

# Pick a file
inlog = utilFunctions.pickNestedFile(inputfolder,
	    ['.trashes', '.DS_Store', 'thumbs.db'])
fname = inlog.split('/')[-1]
path = "/".join(inlog.split('/')[:-1])
print "Path to file "+inlog
print "Name of file "+fname
print "Parent directory "+path
if needlime is True:
	print "TAKING A MOMENT TO CONVERT"


# Pick a line
content = open(inlog).readlines()
if needlime:
	content = convertLimelog(content, 46)
start = random.randint(0, len(content)-1)
print "Starting at line #"+str(start)

# Run with it
selectedlines = []
while length > 0:
	if utilFunctions.quitline(content[start]) is False:
		selectedlines.append(content[start])
		length -= 1
	start += 1
	if start > len(content)-1:
		length = 0
		# implement going to the next available file at a later moment


print selectedlines

processChatLog(selectedlines)


#from lime2input import convertLimeLog
