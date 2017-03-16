# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

from PIL import Image,ImageFont,ImageDraw
import random
from pprint import pprint
import generatePanel
import findEmote
import textwrap
import re
import pyperclip
import StringIO
import ConfigParser
import praw
import sys
import urllib
import os
import json
import getopt
from getch import getch
import utilFunctions
import string




#direct print output to log file
class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("log.txt", "w")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

sys.stdout = Logger()




try:
	urllib.urlretrieve(
		'https://raw.githubusercontent.com/chickens2/pony-comic-generator/master/DEFAULT_ALIAS_DO_NOT_EDIT.cfg',
		'DEFAULT_ALIAS_DO_NOT_EDIT.cfg'
	)
except:
	print 'could not retrieve default alias list, using local version'
config2 = ConfigParser.ConfigParser()
config2.readfp(open('DEFAULT_ALIAS_DO_NOT_EDIT.cfg'))
allNames=dict(config2.items('Aliases'))

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

# Set up names list
allText=""
lines=[]
allNames.update(dict(config.items('Aliases'))) #add aliases from config.cfg, overwrite defaults
allNames2={}
for key in allNames.keys():
	allNames2[key.lower()]=allNames[key].lower()
allNames=allNames2
#print 'final alias list: '
#pprint(allNames)
names={}

# Load things from the config file
selectedBackground=None
fntLarge = ImageFont.truetype(config.get('Fonts','title_font'),int(config.get('Fonts','title_size'))) #used for the title
fntSmall= ImageFont.truetype(config.get('Fonts','cast_font'),int(config.get('Fonts','cast_size'))) #used for the list of characters
anonymousMode=config.get('Options','anonymous_mode').upper()=='TRUE'
uploadImgur=config.get('Options','upload_imgur').upper()=='TRUE'
castIntro=config.get('Options','cast_introduction')
repeatMode=config.get('Options','keep_window_open').upper()=='TRUE'
closeupMultiplier = config.getfloat('Options','closeup_zoom')


# Replace all mentions of nicks with their corresponding pony names
def anonymizeText(text):
	newtext=text
	newWords=[]
	if anonymousMode:
		words=text.split(" ") # can't regex here or else it adds too many spaces around punctuation
		#print 'anonymizing'
		for word in words:
			if len(word)>=4:
				parts=re.findall(r"\w+|[^\w\s]", word, re.UNICODE) # handle 's and names @end of sentences
				word=""
				#print 'considering word '+word
				for part in parts:
					#print 'word part '+part
					if allNames.get(part.lower(),None) is not None:
						#print "removing a name "+part
						part=allNames[part.lower()][1:] # [1:] to get rid of the + in dialogue
					word+=part
			newWords.append(word)
		newtext=" ".join(newWords)
	return newtext

# Pick a title for the strip
def getTitle(specifiedTitle=None):
	if specifiedTitle is not None:
		return specifiedTitle
	random.seed(allText)
	title=None
	#pprint(names)
	if len(lines)==0:
		line=""
	else:
		line=random.choice(lines)
		words=line['text'].split(" ")
		if len(words)>5:
			words=words[-5:]
		while len(words)>2 and random.random()>0.4:
			print words[0]
			del words[0]
			#print 'words:'
			#pprint(words)
		title=string.capwords(" ".join(words))
		#title=textwrap.wrap(title, width=15)
		print 'title '+str(title)
	return title

# Makes the title panel
def createTitlePanel(panelSize):
	title=getTitle()
	img = Image.new("RGBA", panelSize, (255,255,255)) # white background
	d = ImageDraw.Draw(img)
	newh=utilFunctions.drawCenteredText(25,title,d,fntLarge,panelSize)
	newh+=17
	spacing=15
	d.text((spacing,newh), castIntro, font=fntSmall, fill=(0,0,0,255)) # black text
	newh+=spacing
	print 'title panel???'
	for key,value in names.iteritems():
		text=value[1:]
		moreSpacing=0
		if not anonymousMode:
			text=text+" as "+key
		filepath='tagicons/'+value+'.png'
		print 'icon filepath: '+str(filepath)
		if os.path.isfile(filepath):
			moreSpacing=15
			profile=Image.open(filepath).convert('RGBA')
			box=(0,newh,profile.size[0],newh+profile.size[1])
			img.paste(profile,box,mask=profile)
		d.text((spacing+moreSpacing+5,newh), text, font=fntSmall, fill=(0,0,0,255)) # black text
		newh+=spacing+moreSpacing
	generatePanel.drawBorder(img)
	return img#img.show()


prevNames=[] # not sure what this is doing here

#
def createNextPanel(txtLines, panelSize, smallPanels, nameorder, selectedBackground, closeup=True):
	global prevNames
	dialogueOptions=[0]
	generatePanel.setPS(panelSize,"generateComic:createNextPanel")
	print 'nameorder: '+str(nameorder)
	print 'gppanelsize '+str(generatePanel.panelSize)+" "+str(panelSize)
	if len(txtLines)>1 and txtLines[1]['name'] != txtLines[0]['name'] and generatePanel.hasRoomForDialogue2(txtLines[0]['text'],txtLines[1]['text'] ):
		dialogueOptions.append(1)
		if len(txtLines)>2 and txtLines[2]['name'] != txtLines[1]['name'] and txtLines[0]['name'] != txtLines[2]['name'] and generatePanel.hasRoomForDialogue3(txtLines[0]['text'],txtLines[1]['text'],txtLines[2]['text'] ):
			dialogueOptions.append(2)
	random.seed(str(txtLines))
	dialogueChoice=random.choice(dialogueOptions)
	panel=None

	currentNames=[]
	print 'prevnames to start '+str(dialogueChoice)+" "+str(range(dialogueChoice))
	pprint(prevNames)
	for i in range(dialogueChoice+1):
		name=txtLines[i]['name']
		print 'should be removing name '+name
		if name in prevNames: prevNames.remove(name)
		currentNames.append(name)
	print 'prevnames after'
	pprint(prevNames)
	for name in prevNames:
		if dialogueChoice>=2:
			break
		else:
			dialogueChoice+=1
			txtLines.insert(0,{'name':name,'text':''})
			#currentNames.append(name)
	print 'txtLines: '
	pprint(txtLines)
	if dialogueChoice==0:
		panel=generatePanel.drawPanel1Character(txtLines[0]['name'],txtLines[0]['text'],selectedBackground,iscloseup=closeup)
		del txtLines[0]
	if dialogueChoice==1:
		print 'iscorrectorder: '+str(utilFunctions.isCorrectOrder(txtLines[0],txtLines[1],nameorder))
		if utilFunctions.isCorrectOrder(txtLines[0],txtLines[1],nameorder):
			panel=generatePanel.drawPanel2Characters(txtLines[0]['name'],txtLines[1]['name'],txtLines[0]['text'],txtLines[1]['text'],selectedBackground,iscloseup=closeup)
		else:
			panel=generatePanel.drawPanel2Characters(txtLines[1]['name'],txtLines[0]['name'],txtLines[0]['text'],txtLines[1]['text'],selectedBackground,textOrder=1,iscloseup=closeup)
		del txtLines[0]
		del txtLines[0]
	if dialogueChoice==2:
		panel=generatePanel.drawPanel3Characters(txtLines[0]['name'],txtLines[1]['name'],txtLines[2]['name'],txtLines[0]['text'],txtLines[1]['text'],txtLines[2]['text'],selectedBackground,iscloseup=closeup)
		del txtLines[0]
		del txtLines[0]
		del txtLines[0]
	prevNames=currentNames
	print 'returning panel '+str(panel)+" "+str(dialogueChoice)
	return panel

# selects which background image to use
def selectBackground(seed, specifiedBackground=None):
	random.seed(seed)
	if specifiedBackground is not None: # let command-line switches specify a background
		print "Using pre-selected background"
		return specifiedBackground
	BAD_FILES=config.get('Ignore','banned_backgrounds').split()
	if config.has_section('Backgrounds')==False or config.options('Backgrounds')==[]:
		return utilFunctions.pickNestedFile('backgrounds',BAD_FILES)
	else:
		folderTable={}
		for folder in config.options('Backgrounds'):
			folderTable[folder]=config.getint('Backgrounds',folder)
		directory=utilFunctions.weightedDictPick(utilFunctions.genProbabilityDict(folderTable))
		return utilFunctions.pickNestedFile('backgrounds/'+directory,BAD_FILES)

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

# processes the chat log for comic generation
def processChatLog(file, specifiedBackground=None, specifiedTitle=None):
	global lines
	global allNames
	global transform_D
	global undoTransform_D
	transform_D,undoTransform_D = utilFunctions.genTransformDict()
	#findEmote.defaultSeed="".join(file)
	print 'original allnames:'
	pprint(allNames)
	text=""
	mostInARow=1
	currentName=None
	currentInARow=1
	nameOrder=[]
	ponylist=[]
	for line in file:
		#if 'Raribot' in line or '> ~' in line:
		#	continue
		line=line.strip()
		line=line.strip('\n')
		text+=line
		print 'line:'+line
		if line[:2]=="* " and quitline(line) is False:
			line=line[2:]
			line='<'+line[:line.index(' ')]+'> *'+line[line.index(' ')+1:]+'*'
			print 'new line '+line
		if line.count('<')<1 or line.count('>')<1:
			continue
		name=utilFunctions.findBetween(line,'<','>').lower()
		if name not in nameOrder:
			nameOrder.append(name)
		pony=None
		if name not in allNames:
			print 'name '+str(name)+' not in allnames'
			horse_increment = 1
			while horse_increment != -2:
				pony=findEmote.getProceduralPony(name*horse_increment)
				if pony not in ponylist:
					names[name]=pony
					allNames[name]=pony
					ponylist.append(pony)
					horse_increment = -2
				else:
					horse_increment = horse_increment + 1
					print 'pony '+pony+' is already in use; picking a new horse'
		else:
			print 'name '+str(name)+' was in allnames'
			names[name]=allNames[name]
			pony=names[name]
			ponylist.append(pony)
		print 'name: '+name
		line=line[line.index('>')+2:]
		lines.append({"pony":pony,"name":name,"text":line})


		if name==currentName:
			currentInARow+=1
			if currentInARow>mostInARow:
				mostInARow=currentInARow
		else:
			currentInARow=1
		currentName=name
	findEmote.defaultSeed=text

	#this is a bad hack probably but idk how else to do it without adding a million extra parameters everywhere
	print 'the final names list: '
	pprint(names)
	print 'Empty names? '+str(names=={})
	generatePanel.names=names
	print 'most in a row: '+str(mostInARow)
	for line in lines:
		if anonymousMode:
			line['text']=anonymizeText(line['text'])
	#print 'lines:'
	#pprint(lines)
	#return
	selectedBackground=selectBackground(text, specifiedBackground)
	print "Background is "+selectedBackground
	#pprint(names)
	global allText
	allText=text
	#print 'at1'+str(allText)+'^'
	if mostInARow>3:
		smallPanels=True
		panelSize=(200,200)
	else:
		smallPanels=False
		panelSize=(300,300)

	tp=createTitlePanel(panelSize)
	print 'generatecomic panelsize: '+str(panelSize)
	#tp.show()
	panels=[]
	panels.append(tp)
	txtLines=list(lines)
	while len(txtLines)>0:
		panels.append(createNextPanel(txtLines,panelSize,smallPanels,nameOrder,selectedBackground))
	panelsAcross=2
	if smallPanels:
		panelsAcross=3
	if names=={}: #if there's no valid text
		panels.append(generatePanel.drawPanelNoDialogue({},selectedBackground,text+str(len(panels))))

	#if it needs an establishing shot with no dialogue
	if len(panels)%panelsAcross!=0 or names=={}:
		panels.insert(1,generatePanel.drawPanelNoDialogue(nameOrder[:min(3,len(nameOrder))],selectedBackground,text+str(len(panels))))
	else: #otherwise redo the first panel as zoomed out
		txtLines2=list(lines)
		del panels[1]
		panels.insert(1,createNextPanel(txtLines2,panelSize,smallPanels,nameOrder,selectedBackground,closeup=False))

	#if there still aren't enough panels, pad the end
	while len(panels)%panelsAcross!=0 and names!={}:
		panels.append(generatePanel.drawPanelNoDialogue(prevNames,selectedBackground,text+str(len(panels))))

	maxWidth=panelSize[0]*panelsAcross
	currentHeight=0
	currentWidth=0
	img=Image.new('RGBA',(maxWidth,panelSize[1]*len(panels)/panelsAcross))
	print 'comic dimensions: '+str(img.size)
	print 'small panels: '+str(smallPanels)
	print 'panels:'
	pprint(panels)
	for panel in panels:
		panel=utilFunctions.possiblyTransform(panel,999) # Around 1/200 strips will have a flipped panel
		box=(currentWidth,currentHeight,currentWidth+panel.size[0],panel.size[1]+currentHeight)
		print 'making panel at: '+str(box)
		img.paste(panel,box)
		currentWidth+=panel.size[0]
		if currentWidth>=maxWidth:
			currentWidth=0
			currentHeight+=panel.size[1]
	#img.show()
	img=utilFunctions.possiblyTransform(img,420) # Rotating the entire comic should be rarest of all
	img.save("comic.jpg","JPEG")



