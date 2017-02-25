import numpy as np
import cv2
import sys
import glob

print(glob.glob(sys.argv[1]))

for filename in glob.glob(sys.argv[1]):
	#print(filename)
	
	try: #Hey, at least there is some error handling.
		img=cv2.imread(filename) #Read the image
	except:
		continue #Unless you can't. Then skip it.
	outimg=np.copy(img)

	red,green,blue=cv2.split(img) #split the image into components.
	testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
	testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY_INV) #Run a threshold to find only white lines. Interestingly, ret is the image here.
	try:
		cv2.imshow('ThresholdNoErode',ret) #Threshold. Flips black and white.
	except:
		pass
	dump,contours,hierarchy=cv2.findContours(ret,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE) #Get contours in image in a list.
	contours.sort(key=cv2.contourArea,reverse=True) #Sort them by area. Trust me. Saves time because there are a ton of contours with 0 area.
	contour=0 #Iterator
	squares=[] #List of squares to add to.
	while(contour<len(contours) and cv2.contourArea(contours[contour])>100): #Loop until area is too small or all are done
		#print cv2.contourArea(contours[contour])
		epsilon = 0.01*cv2.arcLength(contours[contour],True) #Set up for simplifying contours
		contours[contour]=cv2.approxPolyDP(contours[contour],epsilon,True) #Actually simplifying
		
		if(len(contours[contour])==4): #If the simplified version has 4 sides
			cv2.polylines(img,[contours[contour]],True,(0,255,0)) #Draw it
			squares.append(contours[contour]) #And mark it as a square
		contour+=1
	print(contour,len(squares))
	for square in squares:
		test=cv2.arcLength(square,True)
		print(abs((test*test/16)/cv2.contourArea(square)))

	print("")
	try:
		cv2.imshow("hi",img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	except:
		pass
