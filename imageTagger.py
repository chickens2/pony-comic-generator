import iteratemotes
import msvcrt
import sys
import findEmote
from PIL import Image,ImageFont,ImageDraw
daynum=31
print 'enter emote tag: '
tag=raw_input()
index=0
for emote in findEmote.emotesByPony[tag]:
	print emote
	emoteImg=findEmote.getEmote(emote)
	emoteImg.save("temp.jpg","JPEG")
	iteratemotes.processData(emote)
	index+=1
	print 'tsm:'+str(iteratemotes.totalSelectionsMade)+" "+str(iteratemotes.totalSelectionsMade%(iteratemotes.NUM_SELECTIONS_EACH_IMAGE))
	if iteratemotes.totalSelectionsMade>0 and iteratemotes.totalSelectionsMade%(5*iteratemotes.NUM_SELECTIONS_EACH_IMAGE)==0:
		print 'do you want to save (y/n):'
		while True:
			charused=msvcrt.getch()
			if charused=='y':
				iteratemotes.saveData()
				break
			if charused=='n':
				sys.exit()
iteratemotes.saveData()