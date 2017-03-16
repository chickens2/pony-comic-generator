# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import makeComic
import pyperclip
import random
import sys
import StringIO
from imgurpython import ImgurClient
import ConfigParser
from PIL import Image, ImageFont, ImageDraw

#command line options
textFileChat=None
specifiedBackground=None
specifiedTitle=None
nextToFill=None
for arg in sys.argv:
	if arg[0]=='-':
		nextToFill=arg[1:].lower()
	else:
		if nextToFill is not None:
			if nextToFill[0]=='f':
				textFileChat=arg
			if nextToFill[0]=='b':
				specifiedBackground=arg
			if nextToFill[0]=='t':
				specifiedTitle=arg
		nextToFill=None
print 'chat from log: '+str(textFileChat)

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

# Load things from the config file
selectedBackground=None
fntLarge = ImageFont.truetype(config.get('Fonts','title_font'),int(config.get('Fonts','title_size'))) #used for the title
fntSmall= ImageFont.truetype(config.get('Fonts','cast_font'),int(config.get('Fonts','cast_size'))) #used for the list of characters
anonymousMode=config.get('Options','anonymous_mode').upper()=='TRUE'
uploadImgur=config.get('Options','upload_imgur').upper()=='TRUE'
castIntro=config.get('Options','cast_introduction')
repeatMode=config.get('Options','keep_window_open').upper()=='TRUE'
closeupMultiplier = config.getfloat('Options','closeup_zoom')

uploadReddit=None
reddit = None
if config.has_section('praw') and len(config.get('praw','clientid'))>2:
	#print 'praw stuff:'+config.get('praw','clientid')+"^"
	uploadReddit=config.get('praw','upload')
	reddit = praw.Reddit(client_id=config.get('praw','clientid'),
					client_secret=config.get('praw','clientsecret'),
					user_agent='user agent',
					username=config.get('praw','username'),
					password=config.get('praw','password'))
	print 'reddit credentials:'+str(config.get('praw','clientsecret'))+" "+config.get('praw','clientid')

imgareio = '174becf08a64efc'
imgscrioertu = 'c47422a4a3a7a4aab366b88634bcc03a0ffcaa60'
client = ImgurClient(imgareio, imgscrioertu)

chatfile=None
if textFileChat is None:
	clipboard=pyperclip.paste().encode('utf8')
	print 'clipboard is: \n'+str(clipboard)
	chatfile=StringIO.StringIO(clipboard)
	random.seed(clipboard)
else:
	chatfile=open(textFileChat).readlines()
	random.seed(open(textFileChat))
makeComic.processChatLog(chatfile, specifiedBackground, specifiedTitle)
if uploadImgur:
	image=client.upload_from_path('comic.jpg')
	pyperclip.copy(image['link'])
	print image['link']
	if uploadReddit:
		thetitle=getTitle()
		print 'title '+thetitle+" link "+image['link']
		reddit.subreddit("beniscity").submit(title=thetitle,url=image['link'])
if repeatMode:
	print 'press any key to continue'
	g=getch()()