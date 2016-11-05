import numpy as np
import cv2
import sys
import glob
print sys.argv[1]
for filename in glob.glob(sys.argv[1]):
	print filename
	try:
		img=cv2.imread(filename)
	except:
		continue
	gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	corners=cv2.goodFeaturesToTrack(gray,70,0.5,10)
	corners = np.int0(corners)
#for i in corners:
#	x,y=i.ravel()
#	cv2.circle(img,(x,y),7,255,3)
	harris=cv2.cornerHarris(np.float32(gray),20,11,0.04)
	harris=cv2.dilate(harris,None)
	red,green,blue=cv2.split(img)
	testgray=np.minimum(blue,red)
	testgray=np.minimum(testgray,green)
	#ret=cv2.adaptiveThreshold(testgray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,13,-7)
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY)
	ret=cv2.morphologyEx(ret,cv2.MORPH_ERODE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
	#ret=cv2.Canny(ret,120,255,apertureSize=3)
	lines=cv2.HoughLinesP(ret,1,np.pi/180,1000,300,100)
	for x0,y0,x1,y1 in lines[0]:
		cv2.line(img,(x0,y0),(x1,y1),(0,0,255),2)
	#img[harris>0.01*harris.max()]=[0,0,255]
	cv2.namedWindow("Threshold?", cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty("Threshold?", cv2.WND_PROP_FULLSCREEN,cv2.cv.CV_WINDOW_FULLSCREEN)
	cv2.imshow('Threshold?',ret)
	cv2.imshow('image',img)
	#cv2.imshow('testcolor',testgray)
	print np.array_equal(gray,testgray)
	#cv2.imshow('harris',harris)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
