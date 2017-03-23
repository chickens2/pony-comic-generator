# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import io
import sys
import os
import string
import random
from bs4 import BeautifulSoup

junk_files = ['.DS_Store', 'thumbs.db', '.Trashes']


'''
Converts Adium-saved XML chatlogs into something similar to a LimeChat log
Output is "hh:mm:ss name: message" (with the colon omitted for /me statements)
use -l to specify a single file or -o to convert an entire folder and its subdirectories

NOTE 1: this assumes all files within the root folder are either system junk_files or .xml logs
NOTE 2: THIS USES PYTHON3!!!!!  It otherwise crashes when parsing usernames with non-ASCII characters
NOTE 3: This is not exactly the same as native LimeChat logs, since this one actually differentiates /me lines from other lines
'''


# handle the command line options
fileIn = None
folderIn = None
outputfolder = None
nextToFill = None
for arg in sys.argv:
	if arg[0] == '-':
		nextToFill = arg[1:].lower()
	else:
		if nextToFill is not None:
			if nextToFill[0] == 'l':
				fileIn = arg
			if nextToFill[0] == 'd':
				folderIn = arg
			if nextToFill[0] == 'o':
				outputfolder = arg
		nextToFill = None
if (fileIn is not None or folderIn is not None) and outputfolder is None:
	print("Need to know where to put the completed file(s)")
	sys.exit(1)
if fileIn is None and folderIn is None and outputfolder is not None:
	print("Need some input files")
	sys.exit(2)


def convertmessage(msg):
	name = msg.attrs.get('alias',msg['sender'])
	message = msg.div.string
	#print((msg.div.prettify())) # useful for finding where there's a line that needs special handling
	d8time = msg['time']
	# Assumes yyyy-mm-ddThh:mm:ss-zone as the format
	time = d8time[11:19]
	date = d8time[:10]
	if message is None:
		message = ""
		for stripped in msg.div.span.stripped_strings:
			message = message + ' ' + stripped
	msgsep = ""
	# the len(message) > 0 is needed to prevent problems with blank lines that people sent
	if len(message) > 0 and message[0] == '*' and message[-1] == '*': # /me command
		message = message[1:-1]
	else: # normal line
		msgsep = ":"
	return time + ' ' + name + msgsep + ' ' + message + '\n', date


# takes two strings of numbers and compares them, starting with the leftmost digits
def stringlistisgreater(left, right, separator='-'):
	lNums = left.separate(separator)
	rNums = right.separate(separator)
	tstQty = min(len(lNums), len(rNums))
	for loc in range(tstQty):
		if float(lNums[loc]) > float(rNums[loc]):
			return True
	return False


def greaterDate(lft, rt):
	return stringlistisgreater(lft, rt)


def greaterTime(lt, rt):
	return stringlistisgreater(lt, rt, separator=':')


def convertFile(inputfile):
	convertedtext = {}
	# return {},7 # for debugging
	inputsoup = BeautifulSoup(open(inputfile), "lxml")
	linecount = len(inputsoup.chat.contents)
	msglst = inputsoup.find_all('message')
	for msg in msglst:
		newline, linedate = convertmessage(msg)
		if convertedtext.get(linedate, None) is None:
			convertedtext[linedate] = []
		convertedtext[linedate].append(newline)
	return convertedtext, linecount


# When given a file path, only report back the subdirectories of rootdir
def clean_directory_from_filename(fullname, rootdir):
	directorypath = fullname.split('/')[:-1]
	if rootdir[-1] == '/':
		rootdir = rootdir[:-1]
	corefolder = rootdir.split('/')[-1]
	folderloc = directorypath.index(corefolder)
	return '/'.join(directorypath[folderloc+1:])


def convert_and_save(inputfile, outputdirectory, inputpath = None):
	directory = ''
	if inputpath is not None:
		directory = clean_directory_from_filename(inputfile, inputpath)
	outputdirectory = os.path.join(outputdirectory, directory)
	fname = inputfile.split('/')[-1].split(' ')[:-1][0][1:] # Adium naming black magic
	if not os.path.exists(outputdirectory):
		os.makedirs(outputdirectory)

	lines2save, linecount = convertFile(inputfile)

	for day in list(lines2save.keys()):
		nameout = os.path.join(outputdirectory, day + '_' + fname + '.txt')

		if os.path.isfile(nameout):
			print("File "+nameout+" already exists!")
			continue

		outfile = open(nameout, 'w')
		for line in lines2save[day]:
			outfile.writelines(line)
		outfile.close()


	return linecount


def main():
	if fileIn is not None:
		convert_and_save(fileIn, outputfolder, None)
	if folderIn is not None:
		filecount = 0
		linecount = 0
		for path, subdir, files in os.walk(folderIn):
			for name in files:
				if name not in junk_files:
					filecount += 1
					linecount += convert_and_save(
						os.path.join(path, name),
						outputfolder,
						folderIn)
		print(("Processed " + str(linecount) + " lines over " + str(filecount) + " files."))
		sys.exit(0)

if __name__ == "__main__":
	main()