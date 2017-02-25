import numpy as np
import cv2
import sys
import glob
import math

objectpoints=np.array([[[-14.25,-14.25,0]],[[-14.25,14.25,0]],[[14.25,14.25,0]],[[14.25,-14.25,0]]],np.float32) #3d grid square coordinates
objectpoints=objectpoints.reshape(4,3,1) #Needs to be this shape

CameraMatrix=np.array([[811.75165344, 0., 317.03949866],[0., 811.51686214, 247.65442989],[0., 0., 1.]]) #Values found in CalibrationValues.txt
distortionCoefficients=np.array([-3.00959078e-02, -2.22274786e-01, -5.31335928e-04, -3.74777371e-04, 1.80515550e+00]) #Values found in Calibration Values.txt

distortionCoefficients=distortionCoefficients.reshape(5,1) #Needs to be this shape

font = cv2.FONT_HERSHEY_SIMPLEX #Used for drawing text.
camera=0 #Will be used to test camera loading
if(len(sys.argv)<2): #If no arguments passed
	camera=cv2.VideoCapture(0) #Load the webcam
	filenames=[] #Don't give any filenames
else:
	filenames=glob.glob(sys.argv[1]) #Get the filenames from the command
	print(filenames) #Print them, 'cause why not?
exit=0 #Don't stop running yet
while(len(filenames)>0 or not exit): #If there are more files, or we haven't quit yet
	if(len(filenames)>0): #If we're running purely on files
		exit=1 #Make it quit when we're done with files
		filename=filenames.pop(0) #And get the first file in the list
		try: 
			img=cv2.imread(filename) #Read the image
		except:
			continue #Unless you can't. Then skip it.
	elif(camera): #If using webcam
		ret, img = camera.read() #Read from webcam
	else: #If things are weird, just quit
		break
	if(img==None): #Do make sure that there's and image
		break
	outimg=np.copy(img) #Copy the image. Not really needed, but can be nice long term

	red,green,blue=cv2.split(img) #split the image into components.
	testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
	testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
	out,ret=cv2.threshold(testgray,80,255,cv2.THRESH_BINARY) #Run a threshold to find only white lines. Interestingly, ret is the image here.
	try:
		cv2.imshow('Threshold',ret) #Display the thresholded image
	except:
		exit=1 #If that's not working, your screwed. Just give up now.
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
		contour+=1 #Iterate
	print(contour,len(squares)) #Print the # of squares found
	tvecs=[] #Initialize list for output vectors from camera to center of square
	for square in squares:
		square=square.reshape(4,2,1).astype(float) #The points need to be floats, and in a specific shape
		inliers,rvec,tvec=cv2.solvePnP(objectpoints,square,CameraMatrix,distortionCoefficients) #Where the magic happens. Turns gets vector from camera to center of square
		tvecs.append([float(tvec[0]),float(tvec[1]),float(tvec[2])]) #Add vector to list

	index1=0 #Iterator1
	while(index1<len(tvecs)): #Loop through tvecs
		index2=index1+1 #Iterator2 starts where 1 hasn't reached
		while(index2<len(tvecs)): #And loops through tvecs
			tvec=tvecs[index1] #Iterators are indices for tvecs. Get the tvecs from them
			tvec2=tvecs[index2]
			score=math.sqrt(pow(tvec[0]-tvec2[0],2)+pow(tvec[1]-tvec2[1],2)+pow(tvec[2]-tvec2[2],2))/30.5 #Find the distance between the grid square centers in units of 30.5 cm
			if(abs(round(score,0)-score)<.01): #If it is almost exactly on a unit,
				print((score),tvec,tvec2) #print it
				cv2.polylines(img,[squares[index1]],True,(255,0,0)) #Draw both squares
				cv2.polylines(img,[squares[index2]],True,(255,0,0))
			index2+=1 #Iterate
		index1+=1 #Iterate
	print("") #Divider line
	try:
		cv2.imshow("hi",img) #This is mainly to let my borked python3 install, which can't display images, work.
		if(camera): #If we're doing video
			if cv2.waitKey(1) & 0xFF == ord('q'): #Let the program run while waiting for q to be pressed
				break #Exit
		else: #If it's just files,
			cv2.waitKey(0) #Wait for a key to continue on
			cv2.destroyAllWindows() #And remove the old window
	except:
		pass
cv2.destroyAllWindows() #And don't leave silly windows behind.
