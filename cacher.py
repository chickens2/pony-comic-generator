import urllib
import re
import os
from urllib import FancyURLopener
class MyOpener(FancyURLopener):
	version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
myopener = MyOpener()
urllib.URLopener.version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
def slugify(value):
	import unicodedata
	print type(value)
	if not isinstance(value, str):
		value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
		value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
		value = unicode(re.sub('[-\s]+', '-', value))
	else:
		value = re.sub('[^\w\s-]', '', value.strip().lower())
		value = re.sub('[-\s]+', '-', value)
	return value
def getCache(file):
	#fndomain=slugify(domain.decode('unicode-escape'))
	fpurl='cachedData/'+file
	if not os.path.isfile(fpurl):
		return None
	else:
		f=open(fpurl,'r')
		return f.read()
def writeCache(file,data):
	data=str(data)
	fpurl='cachedData/'+file
	newfolder='cachedData'
	if not os.path.exists(newfolder):
		os.makedirs(newfolder)
	f=open(fpurl,'w+')
	f.write(data)
	f.close()
def getUrlFile(url):
	#print 'getting file: '+url
	urlfn=slugify(url)
	fpurl='cachedData/'+urlfn
	if not os.path.isfile(fpurl):
		print 'whats going wrong here: '+url+"^"+fpurl
		urllib.urlretrieve(url,fpurl)
		#data=myopener.open(url).read()
		#writeCache(urlfn,data)
	return fpurl
		