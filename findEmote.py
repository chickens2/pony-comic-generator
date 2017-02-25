# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import json
from pprint import pprint
import os
import random
import urllib
from PIL import Image,ImageFont,ImageDraw
import cacher
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))


#
defaultSeed=config.get('Options','default_seed') #RAND0m_XD or something or whatever
MIN_LENGTH=config.getint('Options','emotional_diversity') #minimum number of emotes for a tag to be valid
emotesByName={}
emotesByPony={}
BANNED_TAGS=config.get('Ignore','banned_tags').split()
emoteMetadata={}
for file in os.listdir('tagAssignments'):
	#print 'tagassignments file:'+file
	with open('tagAssignments/'+file) as data_file:
		data = json.load(data_file)
		emoteMetadata.update(data)
for fn in os.listdir('emotes'):
	data=None
	with open('emotes/'+fn) as data_file:
		data = json.load(data_file)
		for key in data.keys():
			value=data[key]
			if 'Emotes' not in value or '' not in value['Emotes']:
				del data[key]
				continue
			if 'Image' in value['Emotes']['']:
				if 'amazonaws' in value['Emotes']['']['Image']:
					del data[key]
					continue
			else:
				del data[key]
			if 'Offset' in value['Emotes']['']:
				offset=value['Emotes']['']['Offset']
				if offset[0]>0 or offset[1]>0:
					del data[key]
				else:
					offset[0]=offset[0]*-1
					offset[1]=offset[1]*-1
	emotesByName.update(data)
for fn in os.listdir('tags'):
	data=None
	with open('tags/'+fn) as data_file:
		data = json.load(data_file)
	for key, value in data.iteritems():
		if key in emotesByName and len(value)==1:
			emotes=set()
			#print 'tag: '+value[0]
			if value[0][1:] not in BANNED_TAGS:
				if value[0] not in emotesByPony:
					emotesByPony[value[0]]=emotes
				else:
					emotes=emotesByPony[value[0]]
				emotes.add(key)
for key in emotesByPony.keys():
	if len(emotesByPony[key])<MIN_LENGTH:
		del emotesByPony[key]
	#pprint(emotesByPony)

#
def getProceduralPony(seed):
	random.seed(seed)
	pony=random.choice(emotesByPony.keys())
	return pony

#
def getProceduralEmote(seed1,seed2):
	return getRandomEmote(seed2,getProceduralPony(seed1))

#
def getEmote(emoteName):
	data=emotesByName[emoteName]
	url=data['Emotes']['']['Image']
	offset=[0,0]
	if 'Offset' in data['Emotes']['']:
		offset=data['Emotes']['']['Offset']
	#offset[0]=offset[0]*-1
	#offset[1]=offset[1]*-1
	#if offset[0]<0 or offset[1]<1:
	#	return None
	size=data['Emotes']['']['Size']
	print 'emotename: '+emoteName
	pprint(data)
	print url
	if 'http:' not in url:
		url='http:'+url
	imgloc=cacher.getUrlFile(url)
	fullImage=Image.open(imgloc).convert('RGBA')
	#urllib.urlretrieve(url,'temp.png')
	#fullImage=Image.open("temp.png").convert('RGBA')
	print offset
	print size
	fullImage=fullImage.crop((offset[0],offset[1],offset[0]+size[0],offset[1]+size[1]))
	if emoteName in emoteMetadata:
		data=emoteMetadata[emoteName]
		if 'right' in data:
			print 'findemote flipping image'
			fullImage=fullImage.transpose(Image.FLIP_LEFT_RIGHT)
	return fullImage

#
def getRandomEmote(seed,pony=None):
	global defaultSeed
	if len(seed)<1:
		seed=defaultSeed
	if pony is None:
		pony=random.choice(emotesByPony.keys())
	print pony
	emote=None
	emoteNames=list(emotesByPony[pony])
	#while emote is None and len(emoteNames)>0:
	print 'randomly choosing emote from list of '+str(len(emoteNames))+" with seed "+str(seed)
	random.seed(seed)
	emoteName=random.choice(emoteNames)
	print 'selected emote: '+emoteName
	random.seed()
	emote=getEmote(emoteName)
		#emoteNames.remove(emote)
	return emote

# Other code

#image=getProceduralEmote("pondy")
#image.show()
