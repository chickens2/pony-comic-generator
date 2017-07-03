from shutil import copyfile
import os
import subprocess
from subprocess import DEVNULL, STDOUT, check_call
import compareImages
os.rename('../config.cfg','../config_orig.cfg')
copyfile('testconfig.cfg','../config.cfg')

similar=0
for fn in os.listdir('testLogs'):
	print(fn)
	p = subprocess.Popen(["python", "generateComic.py", '-f',"testSystem/testLogs/"+fn], cwd='..',stdout=DEVNULL, stderr=STDOUT)
	p.wait()
	copyfile('../comic.jpg','testResults/'+fn+'.jpg')
	difference=compareImages.compareImages('testResults/'+fn+'.jpg','defaultResults/'+fn+'.jpg')
	print('image is '+str(difference)+'% different than the default')
	if difference<3:
		print('TEST PASS')
		similar+=1
	else:
		print('TEST FAIL')
		
print(str(similar)+'/'+str(len(os.listdir('testLogs')))+' tests successful')

os.remove('../config.cfg')
os.rename('../config_orig.cfg','../config.cfg')
