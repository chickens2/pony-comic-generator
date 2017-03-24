# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import pyperclip
import random
import sys
import io
from imgurpython import ImgurClient
import configparser
from PIL import Image, ImageFont, ImageDraw
from pprint import pprint
import generatePanel
import findEmote
import textwrap
import re
import praw
import urllib.request, urllib.parse, urllib.error
import os
import json
import getopt
from getch import getch
import utilFunctions
import string


#command line options
textFileChat = None
specifiedBackground = None
specifiedTitle  = None
nextToFill = None
for arg in sys.argv:
	if arg[0] == '-':
		nextToFill = arg[1:].lower()
	else:
		if nextToFill is not None:
			if nextToFill[0] == 'f':
				textFileChat = arg
			if nextToFill[0] == 'b':
				specifiedBackground = arg
			if nextToFill[0] == 't':
				specifiedTitle = arg
		nextToFill = None



config = configparser.ConfigParser(inline_comment_prefixes=(';',))
config.readfp(open('config.cfg'))

# Load things from the config file
selectedBackground=None
fntLarge = ImageFont.truetype(config.get('Fonts','title_font'),int(config.get('Fonts','title_size'))) #used for the title
fntSmall = ImageFont.truetype(config.get('Fonts','cast_font'),int(config.get('Fonts','cast_size'))) #used for the list of characters
anonymousMode = config.get('Options','anonymous_mode').upper()=='TRUE'
uploadImgur = config.get('Options','upload_imgur').upper()=='TRUE'
castIntro = config.get('Options','cast_introduction')
repeatMode = config.get('Options','keep_window_open').upper()=='TRUE'
closeupMultiplier = config.getfloat('Options','closeup_zoom')
allowDuplicates = config.get('Options','allow_duplicates').upper()=='TRUE'
rainbowCast = config.get('Options','rainbow_cast').upper()=='TRUE'
debugprint = config.get('Options','terminal_debug').upper()=='TRUE'
defaultseed = config.get('Options','default_seed')

if debugprint is True:
	print('Verbose mode activated!')
	print(('chat from log: '+str(textFileChat)))


uploadReddit = None
reddit = None
if config.has_section('praw') and len(config.get('praw','clientid'))>2:
	#print 'praw stuff:'+config.get('praw','clientid')+"^"
	uploadReddit=config.get('praw','upload')
	reddit = praw.Reddit(client_id=config.get('praw','clientid'),
					client_secret=config.get('praw','clientsecret'),
					user_agent='user agent',
					username=config.get('praw','username'),
					password=config.get('praw','password'))
	print(('reddit credentials:'+str(config.get('praw','clientsecret'))+" "+config.get('praw','clientid')))

imgareio = '174becf08a64efc'
imgscrioertu = 'c47422a4a3a7a4aab366b88634bcc03a0ffcaa60'
client = ImgurClient(imgareio, imgscrioertu)


#direct print output to log file
class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("log.txt", "w")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

sys.stdout = Logger()


# don't call this unless you're calling this routine directly
if __name__ == "__main__":
	try:
		urllib.request.urlretrieve(
			'https://raw.githubusercontent.com/chickens2/pony-comic-generator/master/DEFAULT_ALIAS_DO_NOT_EDIT.cfg',
			'DEFAULT_ALIAS_DO_NOT_EDIT.cfg'
		)
	except:
		print('could not retrieve default alias list, using local version')
	config2 = configparser.ConfigParser()
	config2.readfp(open('DEFAULT_ALIAS_DO_NOT_EDIT.cfg'))
	allNames=dict(config2.items('Aliases'))

# Set up names list
allText = ""
lines = []
allNames.update(dict(config.items('Aliases'))) #add aliases from config.cfg, overwrite defaults
allNames2 = {}
for key in list(allNames.keys()):
	allNames2[key.lower()] = allNames[key].lower()
allNames = allNames2
if debugprint is True:
	print('final alias list: ')
	pprint(allNames)
names = {}


# Recursively searches through lines of text to
# remove any words found in nameList.keys() and replace
# them with the corresponding value
def anonWord(wordIn, nameList, joiner='', recheck=True):
	masterNameList = {}
	if debugprint is True:
		print(('considering: '+wordIn))

	# Don't bother if the word is too short
	if len(wordIn) < 4:
		return wordIn

	if recheck is False:
		if nameList.get(wordIn.lower(), None) is not None:
			print(("removing a name " + wordIn))
			return nameList[wordIn.lower()][1:] # [1:] to get rid of the + in dialogue
		return wordIn

	if joiner != '': # special case for how to parse space-delimited words
		print("Splitting into words delimited by \'"+joiner+"\'")
		parts = wordIn.split(joiner)
		recheck = True
	else:
		parts = re.findall(r"\w+|[^\w\s]", wordIn, re.UNICODE)
		recheck = False
	newparts = []
	for part in parts:
		newparts.append(anonWord(part, nameList, recheck=recheck))
	return joiner.join(newparts)



# Pick a title for the strip
def getTitle(specifiedTitle=None, seed=None):
	if specifiedTitle is not None:
		return specifiedTitle
	if seed is None:
		seed = defaultseed
	random.seed(seed)
	title = None
	if len(lines) == 0:
		line = ""
	else:
		line = random.choice(list(lines.keys()))
		words = lines[line]['text'].split(" ")
		if len(words) > 5:
			words = words[-5:]
		while len(words) > 2 and random.random() > 0.4:
			print((words[0]))
			del words[0]
		title = string.capwords(" ".join(words))
		#title=textwrap.wrap(title, width=15)
		if debugprint is True:
			print(('title '+str(title)))
	return title

# Makes the title panel
def createTitlePanel(panelSize, castlist, specifiedTitle=None):
	title = getTitle(
		specifiedTitle,
		"+".join(list(castlist.keys())) + ':'.join(list(castlist.values()))
		)
	img = Image.new("RGBA", panelSize, (255,255,255)) # white background
	d = ImageDraw.Draw(img)
	newh = utilFunctions.drawCenteredText(25, title, d, fntLarge, panelSize)
	newh += 17
	spacing = 15
	d.text(
		(spacing, newh),
		castIntro,
		font = fntSmall,
		fill = utilFunctions.rollColor(11, 12, 3, 252)
		) # change to (0,0,0,255) for always black text
	newh += spacing
	print('title panel!!!')

	# Go through the cast list and add them to the title panel
	for name in list(castlist.keys()):
		character = castlist[name][1:]
		moreSpacing = 0
		text = character
		if not anonymousMode:
			text += " as " + name

		# Add a nice cute icon…
		filepath = 'tagicons/' + character + '.png'
		print(('icon filepath: '+str(filepath)))
		# …if it exists
		if os.path.isfile(filepath):
			moreSpacing = 15
			profile = Image.open(filepath).convert('RGBA')
			box = (0, newh, profile.size[0], newh+profile.size[1])
			img.paste(profile, box, mask=profile)

		if rainbowCast is True:
			fntClr = utilFunctions.rollColor(1, 2, 12, 249)
		else:
			fntClr = (0, 0, 0, 255)

		# Print the text
		d.text(
			(spacing + moreSpacing + 5, newh),
			text,
			font = fntSmall,
			fill = fntClr
			) # change to (0,0,0,255) for consistently black text
		newh += spacing + moreSpacing
	generatePanel.drawBorder(img)
	return img#img.show()


prevNames=[] # not sure what this is doing here

#
def createNextPanel(txtLines, panelSize, smallPanels, nameorder, selectedBackground, closeup=True):
	global prevNames
	dialogueOptions = [0]
	generatePanel.setPS(panelSize, "generateComic:createNextPanel")
	print(('nameorder: '+str(nameorder)))
	print(('gppanelsize '+str(generatePanel.panelSize)+" "+str(panelSize)))
	if  len(txtLines) < 1:
		print("No text sent; drawing empty panel!!")
		return generatePanel.drawPanelNoDialogue(
			{},
			selectedBackground,
			str(len(nameorder))
			)
	if (len(txtLines) > 1 and
			txtLines[1]['name'] != txtLines[0]['name'] and
			generatePanel.hasRoomForDialogue2(txtLines[0]['text'], txtLines[1]['text'])):
		dialogueOptions.append(1)
		if (len(txtLines) > 2 and
				txtLines[2]['name'] != txtLines[1]['name'] and
				txtLines[0]['name'] != txtLines[2]['name'] and generatePanel.hasRoomForDialogue3(
					txtLines[0]['text'],
					txtLines[1]['text'],
					txtLines[2]['text']
				)):
			dialogueOptions.append(2)
	random.seed(str(txtLines))
	dialogueChoice = random.choice(dialogueOptions)
	panel = None

	currentNames = {}
	prevNames = {}
	print(('prevnames to start '+str(dialogueChoice)+" "+str(list(range(dialogueChoice)))))
	pprint(prevNames)
	for i in range(dialogueChoice + 1):
		name = txtLines[i]['name']
		pony = txtLines[i]['pony']
		print(('should be removing name '+name))
		if name in list(prevNames.keys()):
			prevNames.pop(name)
		currentNames[name] = pony
	print('prevnames after')
	pprint(prevNames)

	for name in list(prevNames.keys()):
		if dialogueChoice >= 2:
			break
		else:
			dialogueChoice += 1
			txtLines.insert(0, {'name':name, 'text':'', 'pony':allNames[name]})
			#currentNames.append(name)
	print('txtLines: ')
	pprint(txtLines)

	for line in txtLines:
		if line.get('pony', None) is None:
			raise ModuleNotFoundError(str(line)+" does not contain a pony!!!!!!  Quitting.")
			sys.exit(7)

	if dialogueChoice == 0:
		panel = generatePanel.drawPanel1Character(
			txtLines[0]['pony'],
			txtLines[0]['text'],
			selectedBackground,
			iscloseup=closeup
			)
		del txtLines[0]
	if dialogueChoice == 1:
		print(('iscorrectorder: ' + str(utilFunctions.isCorrectOrder(
			txtLines[0],
			txtLines[1],
			nameorder
			))))
		if utilFunctions.isCorrectOrder(txtLines[0], txtLines[1], nameorder):
			panel = generatePanel.drawPanel2Characters(
				txtLines[0]['pony'],
				txtLines[1]['pony'],
				txtLines[0]['text'],
				txtLines[1]['text'],
				selectedBackground,
				iscloseup=closeup
				)
		else:
			panel = generatePanel.drawPanel2Characters(
				txtLines[1]['pony'],
				txtLines[0]['pony'],
				txtLines[0]['text'],
				txtLines[1]['text'],
				selectedBackground,
				textOrder=1,
				iscloseup=closeup
				)
		del txtLines[0]
		del txtLines[0]
	if dialogueChoice == 2:
		panel = generatePanel.drawPanel3Characters(
			txtLines[0]['pony'],
			txtLines[1]['pony'],
			txtLines[2]['pony'],
			txtLines[0]['text'],
			txtLines[1]['text'],
			txtLines[2]['text'],
			selectedBackground,
			iscloseup=closeup
			)
		del txtLines[0]
		del txtLines[0]
		del txtLines[0]
	prevNames = currentNames
	print(('returning panel '+str(panel)+" "+str(dialogueChoice)))
	return panel

# selects which background image to use
def selectBackground(seed, specifiedBackground=None):
	if seed is None:
		seed = defaultseed
	random.seed(seed)
	if specifiedBackground is not None: # let command-line switches specify a background
		if debugprint is True:
			print("Using pre-selected background")
		return specifiedBackground
	BAD_FILES = config.get('Ignore', 'banned_backgrounds').split()
	if config.has_section('Backgrounds') is False or config.options('Backgrounds') == []:
		return utilFunctions.pickNestedFile('backgrounds', BAD_FILES)
	else:
		folderTable = {}
		for folder in config.options('Backgrounds'):
			folderTable[folder] = config.getint('Backgrounds', folder)
		directory = utilFunctions.weightedDictPick(utilFunctions.genProbabilityDict(folderTable))
		if debugprint is True:
			print(folderTable)
			print((utilFunctions.genProbabilityDict(folderTable)))
			print(("Choosing from directory " + directory))
		return utilFunctions.pickNestedFile('backgrounds/' + directory, BAD_FILES)

# check for joined/quit messaegs and remove them
def quitline(line):
	quitmessage = [
		'(Quit:',
		'has joined (',
		'has left IRC (',
		'has changed mode:',
		'You have joined',
		'set the topic'
	]
	for msg in quitmessage:
		if msg in line:
			return True
	return False

#
def cleanupline(linein, namelist):
	# Skip Raribot commands
	#if 'Raribot' in linein or '> ~' in linein:
	#	continue

	# Cleanup the line
	linein = linein.strip()
	linein = linein.strip('\n')
	if debugprint is True:
		print(('line:'+linein))

	# Process /me commands
	if linein[:2] == "* " and quitline(linein) is False:
		linein = linein[2:]
		linein = '<' + linein[:linein.index(' ')] + '> *' + linein[linein.index(' ')+1:] + '*'
		if debugprint is True:
			print(('new /me linein '+linein))

	# Throw out malformed lineins
	if linein.count('<')<1 or linein.count('>')<1:
		return None

	# Determine the nick
	name = utilFunctions.findBetween(linein, '<', '>').lower()
	if name not in namelist:
		namelist.append(name)

	return {"name":name, "text":linein[linein.index('>')+2:]}


# namelist is an output variable
# returns the number largest number of lines in a row a single nick says
def processLines(file, namelist):
	linenumber = 1
	lines = {}
	for line in file:
		lines[linenumber] = cleanupline(line, namelist)
		if lines[linenumber] is not None:
			linenumber += 1
	return lines


#
def getPonyList(namelist, presetList = None):
	horse_assignments = {}
	processedNicks = [] # exists to eliminate repeated calls to list(horse_assignments.keys())
	assignedPonies = [] # exists to eliminate repeated calls to list(horse_assignments.values())

	# 1st round: assign ponies from the preset list
	for nick in namelist:
		if nick in processedNicks:
			continue
		if nick in list(presetList.keys()):
			processedNicks.append(nick)
			horse_assignments[nick] = presetList[nick]
			assignedPonies.append(presetList[nick])

	print("Pre-assigned ponies "+str(assignedPonies)+" for nicks "+str(processedNicks))

	# 2nd round: assign ponies to the rest of the nicks
	for nick in namelist:
		if nick in processedNicks:
			continue
		pony = findEmote.select_horse(nick, assignedPonies, unique=(allowDuplicates==False))
		horse_assignments[nick] = pony
		assignedPonies.append(pony)
		processedNicks.append(nick)

	return horse_assignments


# lines is an output variable
def ponies2lines(ponylist, lines):
	currentName = None
	mostInRow = 0
	currentInRow = 1

	# The next 3 lines are the minimal functionality; everything else here is for tracking
	for line in list(lines.values()):
		name = line["name"]
		line["pony"] = ponylist[name]

		# Tracking for other uses later
		if name == currentName:
			currentInRow += 1
			if currentInRow > mostInRow:
				mostInRow = currentInRow
		else:
			currentInARow = 1
		currentName = name

	return mostInRow



# processes the chat log for comic generation
def processChatLog(file, specifiedBackground=None, specifiedTitle=None, debugprint=False):
	global lines
	global allNames
	global transform_D
	global undoTransform_D
	transform_D,undoTransform_D = utilFunctions.genTransformDict()
	if debugprint is True:
		print('original allnames:')
		pprint(allNames)
	text = ''.join(file)
	findEmote.defaultSeed = text
	mostInARow = 1
	currentInARow = 1
	nameOrder = []
	linenumber = 1
	ponylist = list(allNames.values())

	lines = processLines(file, nameOrder)
	ponyAssignments = getPonyList(nameOrder, allNames)
	mostInARow = ponies2lines(ponyAssignments, lines)

	generatePanel.names = nameOrder

	if debugprint is True:
		print('the final names list: ')
		pprint(ponyAssignments)
		print('Order of names')
		pprint(nameOrder)
		print(('Empty names? '+str(nameOrder=={})))
		print(('most in a row: '+str(mostInARow)))

	if anonymousMode:
		for line in lines:
			lines[line]['text'] = anonWord(
				lines[line]['text'],
				{**allNames, **ponyAssignments},
				joiner = ' '
				)
			if debugprint is True:
				print("Processed line: "+lines[line]['text'])


	# this is a bad hack probably
	# idk how else to do it without adding a million extra parameters everywhere


	#print 'lines:'
	#pprint(lines)
	#return
	selectedBackground = selectBackground(text, specifiedBackground)
	print(("Background is "+selectedBackground))
	#pprint(names)
	global allText
	allText = text
	#print 'at1'+str(allText)+'^'
	if mostInARow > 3:
		smallPanels = True
		panelSize = (200, 200)
	else:
		smallPanels = False
		panelSize = (300, 300)

	tp = createTitlePanel(panelSize, ponyAssignments, specifiedTitle)
	print(('generatecomic panelsize: '+str(panelSize)))
	#tp.show()
	panels = []
	panels.append(tp)
	txtLines = list(lines.values())
	txtLines2 = list(lines.values()) # needed for redone opening panels
	print(txtLines)
	while len(txtLines) > 0:
		panels.append(createNextPanel(txtLines,
			panelSize,
			smallPanels,
			nameOrder,
			selectedBackground))
	panelsAcross = 2
	if smallPanels:
		panelsAcross = 3


	# Set random seed for the rest of this function
	if len(nameOrder) > 0:
		random.seed(selectedBackground.join(nameOrder))
	else:
		random.seed(defaultseed)

	# if it needs an establishing shot with no dialogue
	# This is the preference for 2-wide comics
	# 3-wide comics should only have an empty opening shot if two extra panels are needed
	print(len(panels), panelsAcross)
	if len(panels) % panelsAcross == 1 or len(nameOrder) == 0:
		print("Adding establishing shot")
		horselist = []
		for name in nameOrder[:min(3,random.randrange(len(nameOrder))+1)]:
			horselist.append(ponyAssignments[name])
		panels.insert(
			1,
			generatePanel.drawPanelNoDialogue(
				horselist,
				selectedBackground,
				text+str(len(panels))
			))
	else: #otherwise redo the first panel as zoomed out
		print("Doing a re-shoot of panel 1")
		del panels[1]
		panels.insert(
			1,
			createNextPanel(
				txtLines2,
				panelSize,
				smallPanels,
				nameOrder,
				selectedBackground,
				closeup=False)
			)

	# if there still aren't enough panels, pad the end
	while len(panels)%panelsAcross != 0 and nameOrder != {}:
		print("Adding an end panel")
		horselist = []
		random.seed(str(prevNames))
		for name in prevNames:
			horselist.append(ponyAssignments[name])
		if len(horselist) > 1 and utilFunctions.rollOdds(2):
			random.shuffle(horselist)
			horselist = horselist[:-1]
		panels.append(generatePanel.drawPanelNoDialogue(
			horselist,
			selectedBackground,
			str(len(panels))
			))

	maxWidth = panelSize[0]*panelsAcross
	currentHeight = 0
	currentWidth = 0
	img = Image.new('RGBA', (maxWidth, panelSize[1]*len(panels)//panelsAcross))
	print(('comic dimensions: ' + str(img.size)))
	print(('small panels: ' + str(smallPanels)))
	print('panels:')
	pprint(panels)
	for panel in panels:
		if panel is None:
			print("Skipping bugged-out panel!!!!!!!")
			continue
		panel = utilFunctions.possiblyTransform(panel, 999) # Around 1/200 strips will have a flipped panel
		box = (
			currentWidth,
			currentHeight,
			currentWidth + panel.size[0],
			panel.size[1] + currentHeight
			)
		print(('making panel at: ' + str(box)))
		img.paste(panel, box)
		currentWidth += panel.size[0]
		if currentWidth >= maxWidth:
			currentWidth = 0
			currentHeight += panel.size[1]
	#img.show()
	img = utilFunctions.possiblyTransform(img, 420) # Rotating the entire comic should be rarest of all
	img.save("comic.jpg", "JPEG")


def main():
	print("Main method")
	chatfile = None
	if textFileChat is None:
		clipboard = pyperclip.paste()
		if debugprint is True:
			print(('clipboard is: \n' + str(clipboard)))
		chatfile = io.StringIO(clipboard).readlines()
		random.seed(clipboard)
	else:
		chatfile = open(textFileChat).readlines()
		random.seed(open(textFileChat))

	processChatLog(chatfile, specifiedBackground, specifiedTitle, debugprint)

	if uploadImgur:
		image = client.upload_from_path('comic.jpg')
		pyperclip.copy(image['link'])
		print((image['link']))
		if uploadReddit:
			thetitle = getTitle()
			print(('title ' + thetitle + " link " + image['link']))
			reddit.subreddit("beniscity").submit(title=thetitle, url=image['link'])
	if repeatMode:
		print('press any key to continue')
		g=getch()()

if __name__ == "__main__":
	main()