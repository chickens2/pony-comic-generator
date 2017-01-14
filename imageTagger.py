# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import iteratemotes
#import msvcrt
import sys
import findEmote
from PIL import Image,ImageFont,ImageDraw
from getch import getch

daynum=31
print 'enter emote tag: '
tag=raw_input()
index=0
emotes=findEmote.emotesByPony[tag]

for emote in emotes:
	print emote
	emoteImg=findEmote.getEmote(emote)
	emoteImg.save("temp.jpg","JPEG")
	iteratemotes.processData(emote)
	index+=1
	print 'progress: '+str(index)+"/"+str(len(emotes))
	print 'tsm:'+str(iteratemotes.totalSelectionsMade)+" "+str(iteratemotes.totalSelectionsMade%(5*iteratemotes.NUM_SELECTIONS_EACH_IMAGE))
	if iteratemotes.totalSelectionsMade>0 and iteratemotes.totalSelectionsMade%(5*iteratemotes.NUM_SELECTIONS_EACH_IMAGE)==0:
		print 'do you want to save (y/n):'
		while True:
			charused=getch()()
			if charused=='y':
				iteratemotes.saveData()
				break
			if charused=='n':
				sys.exit()
iteratemotes.saveData()