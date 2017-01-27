import numpy as np
import cv2
import sys
import glob
import math
import bisect
import operator

#Basic distance function, but returns distance squared because I'm not using a vector class, and sqrt is often not needed.
def distance(a,b):
	return (a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1])

#Taxicab distance function, because it is technically faster. Not used currently, but a possibility if needed.
def taxidistance(a,b):
	return abs(a[0]-b[0])+abs(a[1]-b[1])

#Unused. Because itemgetter.
def sortfunc(a):
	return a[0]

print glob.glob(sys.argv[1]) #print the list of files to run on.

#UNUSED FUNCTION, created in an early attempt to find the grid. It should remove lines that do not share points with other lines. Might have broken since then.
def filterLinesToNowhere(iterations,lines):
	for dummy in range(0,iterations):
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
	return lines
	
#UNUSED FUNCTION, created in an early attempt to find the grid. It should compare a how parallel a line is to every single other line. Might be broken.
def compareLinesToOverall(cornerpoints,lines):
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
	return cornerpoints,lines

#Combines nearby points using a weighted average, and taxicab metric
def combineSimilarPoints(cornerpoints,distance): #cornerpoints is a sorted list of points, distance is the max distance at which to combine
	point1=0 #iterator for first point
	while point1<len(cornerpoints): #iterates through everything
		point2=point1+1 #iterator for second point starts after
		while(abs(cornerpoints[point2][0]-cornerpoints[point1][0])<distance if point2<len(cornerpoints) else False): #Scan until x distance > distance, since the list is sorted. Also, don't let indexes get too high.
			if(abs(cornerpoints[point2][1]-cornerpoints[point1][1])<distance): #Check that the y distance is also too close.
				newpoint=cornerpoints[point2] #Create a new point
				newpoint[0]=newpoint[0]*float(newpoint[2])+cornerpoints[point1][0]*float(cornerpoints[point1][2]) #get total x for weighted average
				newpoint[1]=newpoint[1]*float(newpoint[2])+cornerpoints[point1][1]*float(cornerpoints[point1][2]) #get total y for weighted average
				newpoint[0]=int(newpoint[0]/float(newpoint[2]+cornerpoints[point1][2])) #create weighted average x
				newpoint[1]=int(newpoint[1]/float(newpoint[2]+cornerpoints[point1][2])) #create weighted average y
				newpoint[2]+=cornerpoints[point1][2] #add to the weight
				cornerpoints.append(newpoint) #append the point
				cornerpoints.pop(point2) #remove the old points
				cornerpoints.pop(point1)
				point2-=2 #change the indices accordingly
				point1-=1 #change the indices accordingly
				cornerpoints.sort(key=operator.itemgetter(0,1)) #resort. Probably could be done faster by inserting the new point instead of appending.
			point2+=1 #iterate
		point1+=1 #iterate
	return cornerpoints #return the final list of points

#Finds lines between two points a and b that are shorter than searchlength, and longer than minlength, such that b+the line between a and b is within maxdistance of another point in cornerpoints.
#searchlength and searchdistance help prevent unnecessary iteration.
def findExtendedLines(cornerpoints,searchlength,minlength,searchdistance,maxdistance):
	i=0	#Iterator 1
	lines=[] #Initializing
	keys=[r[0] for r in cornerpoints] #Prep for bisect left.
	while i<len(cornerpoints):	#Iterate 1
		j=i+1	#And create iterator 2
		cornerpoints[i][2]=0	#We're reusing the weights from before, and resetting them. This may be an unnecessary artifact of previous code.
		while(cornerpoints[j][0]-cornerpoints[i][0]<searchlength if j<len(cornerpoints) else False): #Only loop through nearby points
			if(abs(cornerpoints[j][1]-cornerpoints[i][1])<searchlength): #Top boundary on nearby points.
				testvec= [cornerpoints[j][0]-cornerpoints[i][0],cornerpoints[j][1]-cornerpoints[i][1]] #Find the line between a and b as a vector.
				if(testvec[0]*testvec[0]+testvec[1]*testvec[1]>minlength*minlength): #If it is longer than minlength
					k=bisect.bisect_left(keys,cornerpoints[j][0]+testvec[0]-searchdistance,lo=j) #Fancy way to get only points within searchdistance of b+line from a to b
					while(abs(cornerpoints[k][0]-cornerpoints[j][0]-testvec[0])<searchdistance if k<len(cornerpoints) else False): #And then loop through them
						if(pow(cornerpoints[k][1]-cornerpoints[j][1]-testvec[1],2)+pow(cornerpoints[k][0]-cornerpoints[j][0]-testvec[0],2)<maxdistance*maxdistance): #Bounded on top too of course.
							#Debug draws
							#cv2.line(img,(cornerpoints[i][0],cornerpoints[i][1]),(cornerpoints[j][0],cornerpoints[j][1]),(0,255,0),2)
							#cv2.line(img,(cornerpoints[j][0],cornerpoints[j][1]),(cornerpoints[j][0]+testvec[0],cornerpoints[j][1]+testvec[1]),(255,255,0),2)
							if([i,j,0] not in lines): #If the line isn't already included in the list
								lines.append([i,j,0]) #Add it. Note, lines are stored by index in the list of cornerpoints. Odd, but makes it easier to debug.
							if(j<k and [j,k,0] not in lines): #But no duplicates on the second line
								lines.append([j,k,0]) #Same weird way to store lines
							if(k<j and [k,j,0] not in lines): #And coordinate order does matter. Smaller goes first
								lines.append([k,j,0]) #Same weird way to store lines
						k+=1 #Iterate
			j+=1 #Iterate
		i+=1 #Iterate
	return lines #return


#Main loop. Loops through filenames given.
for filename in glob.glob(sys.argv[1]):
	print filename
	
	try: #Hey, at least there is some error handling.
		img=cv2.imread(filename) #Read the image
	except:
		continue #Unless you can't. Then skip it.
	#cv2.imshow('Start Image',img)
	outimg=np.copy(img)
	outimg2=np.copy(img)
	#Here begins the OpenCV transforms. I'm leaving in commented transforms, to help show some of the things I tried, and example syntax. Because this is called Teststuff.py, not Final.py

	#gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #Make the image grayscale using default OpenCV conversion
	red,green,blue=cv2.split(img) #split the image into components.
	testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
	testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels

	#adaptivethresh=cv2.adaptiveThreshold(testgray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,13,-7) #Adaptive threshold. Unused.
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY) #Run a threshold to find only white lines. Interestingly, ret is the image here.
	#cv2.imshow('ThresholdNoErode',ret) #draw the threshold before eroding
	#canny=cv2.Canny(ret,120,255,apertureSize=3)
	#cv2.imshow('Canny',canny)
	ret=cv2.morphologyEx(ret,cv2.MORPH_ERODE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))) #Erode the lines found to make them as thin as possible while still detectable. Increase the size to erode more.

	#Unused possible method for edge finding: Canny + HoughLines. Seemed to break under distortion. Might work with different parameters/After distortion can be eliminated.
	#houghlines=cv2.HoughLinesP(ret,1,np.pi/180,1000,300,100)
	#for x0,y0,x1,y1 in houghlines[0]:
	#	cv2.line(img,(x0,y0),(x1,y1),(255,0,0),2)

	#Where the magic happens. I used harris corner detection because most of the other corner detectors found the _best_ corners (which were on the roombas, not the grid).
	harris=cv2.cornerHarris(np.float32(ret),9,5,0.23)
	harris=cv2.morphologyEx(harris,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))) #Filter out tiny corners.
#   harris=cv2.morphologyEx(harris,cv2.MORPH_DILATE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))) #Alternate way to increase size of found corners. Not needed.
#   harris=cv2.dilate(harris,None)

	#Only problem with harris: It returns an image, not coordinates. I basically make it return onto a black and white image, binary.
	binary=np.zeros((1080,1920),'uint8')
	binary[harris>0.01*harris.max()]=255
	img[harris>0.01*harris.max()]=[0,0,255] #also onto the starting image so I can see it.

	#Then, I run findContours, which was the easiest (probably not best) way to turn small corner blobs into polygons with coordinates.
	contours,hierarchy=cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	cv2.drawContours(img,contours,-1,(0,255,0), 3) #And I draw them too!
	
	#This converts polygons into a point at their center of mass, and adds the point to a master list.
	cornerpoints=[] #This is the master list of the x and y coordinates for points.
	for contour in contours: #Obvious loop is obvious
		point=[0,0,0]	#Need to make sure that point has 3 coordinates, x,y,weight
		for i in range(0,len(contour)): #Loop through all the points in the contour
			point[0]=point[0]*float(point[2])/float(point[2]+1)+float(contour[i][0][0])/float(point[2]+1) #Weighted average of x coords
			point[1]=point[1]*float(point[2])/float(point[2]+1)+float(contour[i][0][1])/float(point[2]+1) #Weighted average of y coords
			point[2]+=1 #Increase the weight
		cornerpoints.append([int(point[0]),int(point[1]),point[2]]) #And append at the end

	cornerpoints.sort(key=operator.itemgetter(0,1)) #Sort by x,y. This makes future operations way faster. Trust me.

	print len(cornerpoints) #Good to give some output.

	cornerpoints=combineSimilarPoints(cornerpoints,30) #Combine nearby points

	#print len(cornerpoints) #Left in for debug.

	#
	lines=findExtendedLines(cornerpoints,150,100,30,20) #Finds lines between a,b such that a+b is near another point in the list.


	lines.sort(key=operator.itemgetter(0,1)) #Sort the lines also. This has less effect

	#TODO: Make this into a function. It finds squares formed by the lines previously found, as long as all four points exist. Also, no duplicates.
	keys=[r[0] for r in cornerpoints] #Makes iterating faster later.
	findthe4thcornerfilter=1 #To run (1) or not to run (0)
	finallines=[] #Output list of lines in squares
	squares=[] #Output list of squares
	squaresNoDups=[] #List of squares with unordered points. Allows for faster duplicate prevention

	if(findthe4thcornerfilter!=0): #If we need to run this
		i=0 #Iterator 1
		while(i<len(lines)): #Iterate over lines
			j=i+1 #Iterator 2
			while(j<len(lines)): #Also over lines

				#This whole block finds two lines that share a point. The shared point is starta/startb. The endpoints are enda, endb
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
				else: #If they don't share a point, iterate
					j+=1
					continue

				pointx=cornerpoints[enda][0]+cornerpoints[endb][0]-cornerpoints[startb][0] #Get the x
				pointy=cornerpoints[enda][1]+cornerpoints[endb][1]-cornerpoints[startb][1] #And y coordinates of the 4th point
				k=bisect.bisect_left(keys,pointx-30,lo=j) #Iterate over points within 30 of the potential 4th point.
				while(abs(cornerpoints[k][0]-pointx)<30 if k<len(cornerpoints) and k!=starta else False): #The actual loop.
					if(pow(cornerpoints[k][1]-pointy,2)+pow(cornerpoints[k][0]-pointx,2)<900): #If they are actually close enough
						tempout=[starta,enda,k,endb] #create a square variable
						#print tempout
						if(set(tempout) not in squaresNoDups): #If it isn't a duplicate
							if(len(squares)==0): 		 #If it is the first,
								#print starta,enda,k,endb #Debug, print a sample
								pass
							squares.append(tempout) #Add it to the list.
							squaresNoDups.append(set(tempout)) #And to the faster dup checking list
						if(lines[i] not in finallines): #Also, add lines to the list of lines
							finallines.append(lines[i]) #Note, indices stored, not coordinates.
						if(lines[j] not in finallines): #And make sure _all_ the lines are on there.
							finallines.append(lines[j]) #Seriously.
						if([enda,k,0] not in finallines):
							finallines.append([enda,k,0])
						if([endb,k,0] not in finallines):
							finallines.append([endb,k,0])
					k+=1 #Iterate
				j+=1 #Iterate
			i+=1 #Iterate
	#print(len(squaresNoDups),len(squares)) #Debug

	#TODO: Make this a function. It finds squares that share an edge, and are highly parallel to all other such squares
	squaretest=1 #Should we do the final test? 1=yes
	finalsquares=[] #Final output list
	if(squaretest!=0): #If we're doing this
		for square in squares: #Loop through squares
			testsquares=[] #Prepare a list of squares that share an edge
			for square2 in squares: #Loop through the squares
				if (len(set(square) & set(square2))==2): #If they share 2 points
					testsquares.append(square2) #Add to the list to test

			parallelscore=0.0 #This is how parallel the current most parallel square is. Higher is better. Max is 4.
			for square3 in testsquares: #For all the other squares
				sharedpoints=[] #List of shared points
				for point in square: #Needs to be generate by iterating
					if(point in square3): #If it is a shared point
						sharedpoints.append([square.index(point),square3.index(point)]) #Append the corresponding points

				loopdir1=sharedpoints[0][0]-sharedpoints[1][0]+2 #Find the direction between the shared points
				loopdir2=sharedpoints[0][1]-sharedpoints[1][1]+2 #So that we loop through corresponding edges, not random order

				if(abs(loopdir1)+abs(loopdir2)==2): #If the lines aren't some weird diagonal.
					startpoint1=sharedpoints[0][0] #Get the starting points
					startpoint2=sharedpoints[0][1] #For looping around the edges of both squares
					score=0.0 #Score counter
					while(True): #Loops through the squares. Probably should be a do while, but whatevs.
						nextpoint1=startpoint1 #Cue the looping
						nextpoint2=startpoint2 #Get the next points
						nextpoint1+=loopdir1 #And move in the loopdirs around the corner indices
						nextpoint2+=loopdir2 #For each square
						nextpoint1=nextpoint1%4 #Also, make sure the indexing isn't weird
						nextpoint2=nextpoint2%4

						vec1=[cornerpoints[square[startpoint1]][0]-cornerpoints[square[nextpoint1]][0],cornerpoints[square[startpoint1]][1]-cornerpoints[square[nextpoint1]][1]] #Get the side vector
						vec2=[cornerpoints[square3[startpoint2]][0]-cornerpoints[square3[nextpoint2]][0],cornerpoints[square3[startpoint2]][1]-cornerpoints[square3[nextpoint2]][1]] #Remember: points need to be retrieved
						
						#print vec1,vec2 #Debug These should be basically identical
						score+=abs((vec1[0]*vec2[0]+vec1[1]*vec2[1])/(math.sqrt(pow(vec1[0],2)+pow(vec1[1],2))*math.sqrt(pow(vec2[0],2)+pow(vec2[1],2)))) #But we use the dot product to score it.
						if(score>parallelscore): #Score is the sum of the absolute value of the cosines of all the differences in corresponding angles of the two squares.
							parallelscore=score #If it is the current biggest, set the maximum
						startpoint1=nextpoint1 #Iterate
						startpoint2=nextpoint2 #Iterate
						if(startpoint1==sharedpoints[0][0]): #If we made it all the way around
							break #Exit

			#print parallelscore #Debug print
			if(parallelscore>3.99): #If it actually is very parallel
				if set(square) not in finalsquares: #And not a duplicate
					finalsquares.append(set(square)) #Add it to the list of squares

	#Unused test code for an opencv function for features. Found too many roomba corners, not grid corners.
	corners=cv2.goodFeaturesToTrack(ret,70,0.75,10)
	corners = np.int0(corners)
	for i in corners:
		x,y=i.ravel()
		cv2.circle(outimg,(x,y),7,255,3)

	
	print len(squares) #Debug print
	print len(finalsquares) #Should be smaller than the 

	lines.sort(key=operator.itemgetter(2))
	#These draw all the lines, and finallines found
	for line in lines:
		point1=cornerpoints[line[0]]
		point2=cornerpoints[line[1]]
		cv2.line(outimg2,(point1[0],point1[1]),(point2[0],point2[1]),(0,255,0),2)#line[2]/lines[-1][2],0),2)
	for line in finallines:
		point1=cornerpoints[line[0]]
		point2=cornerpoints[line[1]]
		cv2.line(outimg2,(point1[0],point1[1]),(point2[0],point2[1]),(0,0,255),2)

	for square in finalsquares: #Loop through and draw the final squares
		for point in square: #But I'm too lazy to order the points
			for point2 in square: #So I just draw all 6 lines
				if(point!=point2):
					cv2.line(img,(cornerpoints[point][0],cornerpoints[point][1]),(cornerpoints[point2][0],cornerpoints[point2][1]),(255,0,0),2) #WHEEE!
			
	for a in range(0,len(cornerpoints)): #I don't know what this does right now. But it helps draw corners? I guess?
		try:
			cornerpoints[a][2]=cornerpoints[a][2]/float(cornerpoints[a][3])
		except:
			cornerpoints[a][2]=0
	cornerpoints.sort(key=operator.itemgetter(2)) #??


	for a in range(len(cornerpoints)-1,-1,-1): #Draw the original found corners, looping backwards, for some reason
		point=cornerpoints[a]
		cv2.circle(img,(int(point[0]),int(point[1])),7,(0,0,255),3)
		cv2.circle(outimg2,(int(point[0]),int(point[1])),7,(0,0,255),3)

	cv2.imshow('Threshold?',ret) #Draw the threshold image
	cv2.imshow('Corners?',binary) #Draw the harris result image
	cv2.imshow('image',img)
	#cv2.imshow('lines and such',outimg2)
	#cv2.imshow('GoodFeaturesToTrack',outimg)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
