import numpy as np
import cv2
import sys
import glob
import math
import bisect
import operator
def taxidistance(a,b):
	return abs(a[0]-b[0])+abs(a[1]-b[1])

def sortfunc(a):
	return a[0]

def distance(a,b):
	return (a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1])

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
	#print cornerpoints
	#print cornerpoints
	print len(cornerpoints)

	dothefilter=30
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
	img[harris>0.01*harris.max()]=[0,0,255]
	i=0
	lines=[]
	keys=[r[0] for r in cornerpoints]
	while i<len(cornerpoints):
		j=i+1
		cornerpoints[i][2]=0
		while(cornerpoints[j][0]-cornerpoints[i][0]<150 if j<len(cornerpoints) else False):
			if(abs(cornerpoints[j][1]-cornerpoints[i][1])<150):
				testvec= [cornerpoints[j][0]-cornerpoints[i][0],cornerpoints[j][1]-cornerpoints[i][1]]
				if(testvec[0]*testvec[0]+testvec[1]*testvec[1]>10000):
				#cv2.line(img,(cornerpoints[i][0],cornerpoints[i][1]),(cornerpoints[i][0]+testvec[0],cornerpoints[i][1]+testvec[1]),(255,0,0),2)				
					k=bisect.bisect_left(keys,cornerpoints[j][0]+testvec[0]-30,lo=j)
					while(abs(cornerpoints[k][0]-cornerpoints[j][0]-testvec[0])<30 if k<len(cornerpoints) else False):
						if(pow(cornerpoints[k][1]-cornerpoints[j][1]-testvec[1],2)+pow(cornerpoints[k][0]-cornerpoints[j][0]-testvec[0],2)<400):
							#print "("+str(pow(cornerpoints[k][1]-cornerpoints[j][1]-testvec[1],2)+pow(cornerpoints[k][0]-cornerpoints[j][0]-testvec[0],2))+")"
							#cv2.line(img,(cornerpoints[i][0],cornerpoints[i][1]),(cornerpoints[j][0],cornerpoints[j][1]),(0,255,0),2)
							#cv2.line(img,(cornerpoints[j][0],cornerpoints[j][1]),(cornerpoints[j][0]+testvec[0],cornerpoints[j][1]+testvec[1]),(255,0,0),2)
							if([i,j,0] not in lines):
								lines.append([i,j,0])
							if(j<k and [j,k,0] not in lines):
								lines.append([j,k,0])
							if(k<j and [k,j,0] not in lines):
								lines.append([k,j,0])
						k+=1
			j+=1
		i+=1
	lines.sort(key=operator.itemgetter(0,1))
	findthe4thcornerfilter=1
	finallines=[]
	squares=[]
	total=0
	if(findthe4thcornerfilter!=0):
		i=0
		while(i<len(lines)):
			j=i+1
			while(j<len(lines)):
				if(lines[i][0] == lines[j][0]):
					starta=lines[i][0]
					startb=lines[j][0]
					enda=lines[i][1]
					endb=lines[j][1]
				elif(lines[i][0] == lines[j][1]):
					starta=lines[i][0]
					startb=lines[j][1]
					enda=lines[i][1]
					endb=lines[j][0]
				elif(lines[i][1] == lines[j][0]):
					starta=lines[i][1]
					startb=lines[j][0]
					enda=lines[i][0]
					endb=lines[j][1]
				elif(lines[i][1] == lines[j][1]):
					starta=lines[i][1]
					startb=lines[j][1]
					enda=lines[i][0]
					endb=lines[j][0]
				else:
					j+=1
					continue
				pointx=cornerpoints[enda][0]+cornerpoints[endb][0]-cornerpoints[startb][0]
				pointy=cornerpoints[enda][1]+cornerpoints[endb][1]-cornerpoints[startb][1]
				k=bisect.bisect_left(keys,pointx-30,lo=j)
				while(abs(cornerpoints[k][0]-pointx)<30 if k<len(cornerpoints) and k!=starta else False):
					if(pow(cornerpoints[k][1]-pointy,2)+pow(cornerpoints[k][0]-pointx,2)<900):
						tempout=[starta,enda,k,endb]
						#print tempout
						if(tempout not in squares):
							if(len(squares)==0):
								print starta,enda,k,endb
							squares.append(tempout)
						if(lines[i] not in finallines):
							finallines.append(lines[i])
						if(lines[j] not in finallines):
							finallines.append(lines[j])
						if([enda,k,0] not in finallines):
							finallines.append([enda,k,0])
						if([endb,k,0] not in finallines):
							finallines.append([endb,k,0])
						total+=1
					k+=1
				j+=1
			i+=1
	squaretest=1
	finalsquares=[]
	if(squaretest!=0):
		for square in squares:
			testsquares=[]
			for square2 in squares[squares.index(square)+1:]:
				if (len(set(square) & set(square2))==2):
					testsquares.append(square2)

			parallelscore=0.0
			for square3 in testsquares:
				sharedpoints=[]
				for point in square:
					if(point in square3):
						sharedpoints.append([square.index(point),square3.index(point)])
				loopdir1=sharedpoints[0][0]-sharedpoints[1][0]+2

				loopdir2=sharedpoints[0][1]-sharedpoints[1][1]+2
				if(abs(loopdir1)+abs(loopdir2)==2):
					startpoint1=sharedpoints[0][0]
					startpoint2=sharedpoints[0][1]
					score=0.0
					while(True):
						nextpoint1=startpoint1
						nextpoint2=startpoint2
						nextpoint1+=loopdir1
						nextpoint2+=loopdir2
						nextpoint1=nextpoint1%4
						nextpoint2=nextpoint2%4

						vec1=[cornerpoints[square[startpoint1]][0]-cornerpoints[square[nextpoint1]][0],cornerpoints[square[startpoint1]][1]-cornerpoints[square[nextpoint1]][1]]
						vec2=[cornerpoints[square3[startpoint2]][0]-cornerpoints[square3[nextpoint2]][0],cornerpoints[square3[startpoint2]][1]-cornerpoints[square3[nextpoint2]][1]]
						
						#print vec1,vec2
						score+=abs((vec1[0]*vec2[0]+vec1[1]*vec2[1])/(math.sqrt(pow(vec1[0],2)+pow(vec1[1],2))*math.sqrt(pow(vec2[0],2)+pow(vec2[1],2))))
						if(score>parallelscore):
							parallelscore=score
						startpoint1=nextpoint1
						startpoint2=nextpoint2
						if(startpoint1==sharedpoints[0][0]):
							break
					#print "done"
			print parallelscore
			if(parallelscore>3.99):
				if set(square) not in finalsquares:
					finalsquares.append(set(square))
	filterlinestonowhere=0
	for dummy in range(0,filterlinestonowhere):
		print len(lines)
		i=0
		j=0
		while i<len(lines):
			j=0
			count=0
			while(j<len(lines)):
				if(i==j):
					j+=1
					continue
				if(lines[j][0]==lines[i][0] or lines[j][1]==lines[i][0]):
					count+=1
					break
				j+=1
			if(count==0):
				lines.pop(i)
			else:
				i+=1
		i=0
		j=0
		print len(lines)
		while i<len(lines):
			j=0
			count=0
			while(j<len(lines)):
				if(i==j):
					j+=1
					continue
				if(lines[j][0]==lines[i][1] or lines[j][1]==lines[i][1]):
					count+=1				
					break
				j+=1
			if(count==0):
				lines.pop(i)
			else:
				i+=1
	parallelicity=0
	print len(lines)
	if(parallelicity!=0):
		for i in range(0,len(lines)):
			point1=cornerpoints[lines[i][0]]
			point2=cornerpoints[lines[i][1]]
			line1=[point1[0]-point2[0],point1[1]-point2[1]]
			for j in range(i+1,len(lines)):
				point1=cornerpoints[lines[j][0]]
				point2=cornerpoints[lines[j][1]]
				line2=[point1[0]-point2[0],point1[1]-point2[1]]
				dotproduct=line1[0]*line2[0]+line1[1]*line2[1]
				dotproduct=dotproduct/(math.sqrt(distance(line1,(0.0,0.0)))*math.sqrt(distance(line2,(0.0,0.0))))
				lines[i][2]+=abs(dotproduct)
				lines[j][2]+=abs(dotproduct)
				cornerpoints[lines[i][0]][2]+=abs(dotproduct)
				cornerpoints[lines[i][1]][2]+=abs(dotproduct)
				cornerpoints[lines[j][0]][2]+=abs(dotproduct)
				cornerpoints[lines[j][1]][2]+=abs(dotproduct)
			if(len(cornerpoints[lines[i][0]])<4):
				cornerpoints[lines[i][0]].append(0)
			else:
				cornerpoints[lines[i][0]][3]+=1
			if(len(cornerpoints[lines[i][1]])<4):
				cornerpoints[lines[i][1]].append(0)
			else:
				cornerpoints[lines[i][1]][3]+=1


	"""	corners=cv2.goodFeaturesToTrack(ret,70,0.75,10)
	corners = np.int0(corners)
	for i in corners:
		x,y=i.ravel()
		cv2.circle(img,(x,y),7,255,3)

	"""
	#print len(finallines)
	print len(squares)
	#print squares[0]
	#print len(set([5,6,7,8]) & set([7,8,9,10]))
	print len(finalsquares)

	lines.sort(key=operator.itemgetter(2))
	"""
	for line in lines:
		point1=cornerpoints[line[0]]
		point2=cornerpoints[line[1]]
		cv2.line(img,(point1[0],point1[1]),(point2[0],point2[1]),(0,255,0),2)#line[2]/lines[-1][2],0),2)
	for line in finallines:
		point1=cornerpoints[line[0]]
		point2=cornerpoints[line[1]]
		cv2.line(img,(point1[0],point1[1]),(point2[0],point2[1]),(0,0,255),2)
	"""
	for square in finalsquares:
		for point in square:
			for point2 in square:
				if(point!=point2):
					cv2.line(img,(cornerpoints[point][0],cornerpoints[point][1]),(cornerpoints[point2][0],cornerpoints[point2][1]),(255,0,0),2)
			
	for a in range(0,len(cornerpoints)):
		try:
			cornerpoints[a][2]=cornerpoints[a][2]/float(cornerpoints[a][3])
		except:
			cornerpoints[a][2]=0
		
	cornerpoints.sort(key=operator.itemgetter(2))
	for a in range(len(cornerpoints)-1,-1,-1):
		point=cornerpoints[a]
		cv2.circle(img,(int(point[0]),int(point[1])),7,(0,0,255),3)
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
