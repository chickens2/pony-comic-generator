from PIL import Image, ImageFont, ImageDraw
def compareImages(image1,image2):
	i1 = Image.open(image1)
	i2 = Image.open(image2)
	if not i1.mode == i2.mode:
		return 100.0
	if not  i1.size == i2.size:
		return 100.0
	 
	pairs = zip(i1.getdata(), i2.getdata())
	if len(i1.getbands()) == 1:
		# for gray-scale jpegs
		dif = sum(abs(p1-p2) for p1,p2 in pairs)
	else:
		dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
	 
	ncomponents = i1.size[0] * i1.size[1] * 3
	return (dif / 255.0 * 100) / ncomponents
	
if __name__ == "__main__":
	print(str(compareImages("testResults/log1.txt.jpg","defaultResults/log1.txt.jpg")))