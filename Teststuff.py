import numpy as np
import cv2
import sys
import glob
import math
import bisect
import operator
def distance(a,b):
	return abs(a[0]-b[0])+abs(a[1]-b[1])

def sortfunc(a):
	return a[0]

def searchfunc(a,b):
	test=(a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1])

print glob.glob(sys.argv[1])
for filename in glob.glob(sys.argv[1]):
	cornerpoints=[]
	print filename
	try:
		img=cv2.imread(filename)
	except:
		continue
	gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	binary=np.zeros((1080,1920),'uint8')
	red,green,blue=cv2.split(img)
	testgray=np.minimum(blue,red)
	testgray=np.minimum(testgray,green)
	#ret=cv2.adaptiveThreshold(testgray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,13,-7)
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY)
	ret=cv2.morphologyEx(ret,cv2.MORPH_ERODE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
	#ret=cv2.Canny(ret,120,255,apertureSize=3)
#	lines=cv2.HoughLinesP(ret,1,np.pi/180,1000,300,100)
#	for x0,y0,x1,y1 in lines[0]:
#		cv2.line(img,(x0,y0),(x1,y1),(255,0,0),2)
	harris=cv2.cornerHarris(np.float32(ret),9,5,0.23)
	harris=cv2.morphologyEx(harris,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
	#harris=cv2.morphologyEx(harris,cv2.MORPH_DILATE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))

	#harris=cv2.dilate(harris,None)
	binary[harris>0.01*harris.max()]=255

	print binary.dtype
	contours,hierarchy=cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(img,contours,-1,(0,255,0), 3)
	for contour in contours:
		point=[0,0,0]
		for i in range(0,len(contour)):
			point[0]=point[0]*float(point[2])/float(point[2]+1)+float(contour[i][0][0])/float(point[2]+1)
			point[1]=point[1]*float(point[2])/float(point[2]+1)+float(contour[i][0][1])/float(point[2]+1)
			point[2]+=1
		cornerpoints.append([int(point[0]),int(point[1]),point[2]])

	cornerpoints.sort(key=operator.itemgetter(0,1))
	#print len(harris)
	print cornerpoints
	#print cornerpoints
	print len(cornerpoints)

	dothefilter=20
	if dothefilter!=0:
		point1=0
		while point1<len(cornerpoints):
			point2=point1+1
			while(abs(cornerpoints[point2][0]-cornerpoints[point1][0])<dothefilter if point2<len(cornerpoints) else False):
				if(abs(cornerpoints[point2][1]-cornerpoints[point1][1])<dothefilter):
					newpoint=cornerpoints[point2]
					newpoint[0]=newpoint[0]*float(newpoint[2])+cornerpoints[point1][0]*float(cornerpoints[point1][2])
					newpoint[1]=newpoint[1]*float(newpoint[2])+cornerpoints[point1][1]*float(cornerpoints[point1][2])
					newpoint[0]=int(newpoint[0]/float(newpoint[2]+cornerpoints[point1][2]))
					newpoint[1]=int(newpoint[1]/float(newpoint[2]+cornerpoints[point1][2]))
					newpoint[2]+=cornerpoints[point1][2]
					cornerpoints.append(newpoint)
					cornerpoints.pop(point2)
					cornerpoints.pop(point1)
					point2-=2
					point1-=1
					cornerpoints.sort(key=operator.itemgetter(0,1))
				point2+=1
			point1+=1
	#print cornerpoints
	#print len(cornerpoints)
	for point in cornerpoints:
		cv2.circle(img,(int(point[0]),int(point[1])),7,255,3)
	img[harris>0.01*harris.max()]=[0,0,255]
	i=0
	lines=[]
	keys=[r[0] for r in cornerpoints]
	while i<len(cornerpoints):
		j=i+1
		
		while(cornerpoints[j][0]-cornerpoints[i][0]<175 if j<len(cornerpoints) else False):
			if(abs(cornerpoints[j][1]-cornerpoints[i][1])<175):
				testvec= [cornerpoints[j][0]-cornerpoints[i][0],cornerpoints[j][1]-cornerpoints[i][1]]
				if(testvec[0]*testvec[0]+testvec[1]*testvec[1]>900):
				#cv2.line(img,(cornerpoints[i][0],cornerpoints[i][1]),(cornerpoints[i][0]+testvec[0],cornerpoints[i][1]+testvec[1]),(255,0,0),2)				
					k=bisect.bisect_left(keys,cornerpoints[j][0]+testvec[0]-30,lo=j)
					while(abs(cornerpoints[k][0]-cornerpoints[j][0]-testvec[0])<30 if k<len(cornerpoints) else False):
						if(abs(cornerpoints[k][1]-cornerpoints[j][1]-testvec[1])<30):
							cv2.line(img,(cornerpoints[i][0],cornerpoints[i][1]),(cornerpoints[j][0],cornerpoints[j][1]),(0,255,0),2)
							cv2.line(img,(cornerpoints[j][0],cornerpoints[j][1]),(cornerpoints[j][0]+testvec[0],cornerpoints[j][1]+testvec[1]),(255,0,0),2)
						k+=1
					
				
			j+=1
		i+=1
	"""	corners=cv2.goodFeaturesToTrack(ret,70,0.75,10)
	corners = np.int0(corners)
	for i in corners:
		x,y=i.ravel()
		cv2.circle(img,(x,y),7,255,3)

	"""

	cv2.namedWindow("Threshold?", cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty("Threshold?", cv2.WND_PROP_FULLSCREEN,cv2.cv.CV_WINDOW_FULLSCREEN)
	cv2.imshow('Threshold?',ret)
	cv2.imshow('Corners?',binary)
	cv2.imshow('image',img)
	#cv2.imshow('testcolor',testgray)
	print np.array_equal(gray,testgray)
	#cv2.imshow('harris',harris)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
