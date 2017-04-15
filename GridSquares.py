import numpy as np
import cv2
import sys
import glob
from operator import itemgetter
import math

def dot(a,b):
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def vecsub(a,b):
	return [a[0]-b[0],a[1]-b[1],a[2]-b[2]]
def distance(a):
	return math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
def scalarmult(a,b):
	return([a[0]*b,a[1]*b,a[2]*b])

squarelength=28.5 #Needs to be a float, in cm of real length of the squares
objectpoints=np.array([[[-squarelength/2,-squarelength/2,0]],[[-squarelength/2,squarelength/2,0]],[[squarelength/2,squarelength/2,0]],[[squarelength/2,-squarelength/2,0]]],np.float32) #3d grid square coordinates
secondObjectCorners=np.array([[[-squarelength/2,0,0]],[[-squarelength/2,squarelength,0]],[[squarelength/2,squarelength,0]],[[squarelength/2,0,0]]],np.float32)
thirdObjectCorners=np.array([[[0,-squarelength/2,0]],[[0,squarelength/2,0]],[[squarelength,squarelength/2,0]],[[squarelength,-squarelength/2,0]]],np.float32)

objectpoints=objectpoints.reshape(4,3,1) #Needs to be this shape
secondObjectCorners=secondObjectCorners.reshape(4,3,1)
thirdObjectCorners=thirdObjectCorners.reshape(4,3,1)
CameraMatrix=np.array([[811.75165344, 0., 317.03949866],[0., 811.51686214, 247.65442989],[0., 0., 1.]]) #Values found in CalibrationValues.txt
distortionCoefficients=np.array([-3.00959078e-02, -2.22274786e-01, -5.31335928e-04, -3.74777371e-04, 1.80515550e+00]) #Values found in Calibration Values.txt

distortionCoefficients=distortionCoefficients.reshape(5,1) #Needs to be this shape

heights=[[0,0],[0,0],[0,0]]
font = cv2.FONT_HERSHEY_SIMPLEX #Used for drawing text.
camera=0 #Will be used to test camera loading
if(len(sys.argv)<2): #If no arguments passed
	camera=cv2.VideoCapture(1) #Load the webcam
	filenames=[] #Don't give any filenames
else:
	filenames=glob.glob(sys.argv[1]) #Get the filenames from the command
	print(filenames) #Print them, 'cause why not?
exit=0 #Don't stop running yet
while(len(filenames)>0 or not exit): #If there are more files, or we haven't quit yet
	heights[2]=heights[1]
	heights[1]=heights[0]
	heights[0]=[0,0]
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
	if(img==None): #Do make sure that there's an image
		break
	outimg=np.copy(img) #Copy the image. Not really needed, but can be nice long term

	red,green,blue=cv2.split(img) #split the image into components.
	testgray=np.minimum(blue,red) #Create a new image with the minimum of b and r channels
	testgray=np.minimum(testgray,green) #Create a new image with minimum of all three channels
	out,ret=cv2.threshold(testgray,120,255,cv2.THRESH_BINARY) #Run a threshold to find only white lines. Interestingly, ret is the image here.
	try:
		cv2.imshow('Threshold',ret) #Display the thresholded image
	except:
		#exit=1 #If that's not working, your screwed. Just give up now.
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
	#print(contour,len(squares)) #Print the # of squares found
	#print(len(img),len(img[0]))
	tvecs=[] #Initialize list for output vectors from camera to center of square
	for square in squares:
		square=square.reshape(4,2,1).astype(float) #The points need to be floats, and in a specific shape
		inliers,rvec,tvec=cv2.solvePnP(objectpoints,square,CameraMatrix,distortionCoefficients) #Where the magic happens. Turns gets vector from camera to center of square
		inliers,rvec2,tvec2=cv2.solvePnP(secondObjectCorners,square,CameraMatrix,distortionCoefficients)
		inliers,rvec3,tvec3=cv2.solvePnP(thirdObjectCorners,square,CameraMatrix,distortionCoefficients)
		#print(distance(vecsub(tvec2,tvec)),distance(vecsub(tvec3,tvec)))
		line1=vecsub(tvec2,tvec)
		line1=scalarmult(line1,1/distance(line1))
		line2=vecsub(tvec3,tvec)
		line2=scalarmult(line2,1/distance(line2))
		tvecs.append([float(tvec[0]),float(tvec[1]),float(tvec[2]),float(line1[0]),float(line1[1]),float(line1[2]),float(line2[0]),float(line2[1]),float(line2[2])]) #Add vector to list

	index1=0 #Iterator1
	#print("")
	while(index1<len(tvecs)): #Loop through tvecs
		index2=0 #Iterator2 starts where 1 hasn't reached
		score=0
		while(index2<len(tvecs)): #And loops through tvecs

			tvec=tvecs[index1] #Iterators are indices for tvecs. Get the tvecs from them
			tvec2=tvecs[index2]
			cross1=[tvec[4]*tvec[8]-tvec[5]*tvec[7],tvec[5]*tvec[6]-tvec[3]*tvec[8],tvec[3]*tvec[7]-tvec[4]*tvec[6]]
			cross2=[tvec2[4]*tvec2[8]-tvec2[5]*tvec2[7],tvec2[5]*tvec2[6]-tvec2[3]*tvec2[8],tvec2[3]*tvec2[7]-tvec2[4]*tvec2[6]]
			cross3=[cross1[1]*cross2[2]-cross1[2]*cross2[1],cross1[2]*cross2[0]-cross1[0]*cross2[2],cross1[0]*cross2[1]-cross1[1]*cross2[0]]

			
			edge=0
			for point in squares[index2]:
				if(point[0][0]==0 or point[0][0]==len(img[0])-1 or point[0][1]==0 or point[0][1]==len(img)-1):
					edge=1
			if(not edge):
				#score+=abs(dot(cross1,cross2))
				score+=1-abs(distance(cross3)/(distance(cross2)*distance(cross1)))
			#score=distance(vecsub(tvec[:3],tvec2[:3]))/30.5 #Find the distance between the grid square centers in units of 30.5 cm
			#print(dot(vecsub(tvec[:3],tvec2[:3]),tvec[3:6]),dot(vecsub(tvec[:3],tvec2[:3]),tvec[6:]),dot(vecsub(tvec2[:3],tvec[:3]),tvec2[3:6]),dot(vecsub(tvec2[:3],tvec[:3]),tvec2[6:]),score)
			
			index2+=1 #Iterate
		tvecs[index1].append(score)
		tvecs[index1].append([squares[index1]])
		index1+=1 #Iterate
	tvecs.sort(key=itemgetter(9),reverse=True)
	if(len(tvecs)>0):
		averageheight=0
		scorethreshold=.95*tvecs[0][9]
		tvecindex=0
		while(tvecs[tvecindex][9]>scorethreshold and tvecindex<len(tvecs)-1):
			thing=tvecs[tvecindex]
			cross=[thing[4]*thing[8]-thing[5]*thing[7],thing[5]*thing[6]-thing[3]*thing[8],thing[3]*thing[7]-thing[4]*thing[6]]
			height=abs(dot(thing[:3],cross)/distance(cross))
			averageheight+=height
			#print dot(vecsub(tvec[:3],tvec2[:3]),tvec[3:6]),dot(vecsub(tvec[:3],tvec2[:3]),tvec[6:]),dot(vecsub(tvec2[:3],tvec[:3]),tvec2[3:6]),dot(vecsub(tvec2[:3],tvec[:3]),tvec2[6:]),score
			#print(thing[9]) #print it
			x=0
			y=0
			for point in thing[10][0]:
				x+=point[0][0]
				y+=point[0][1]
			x=x/4
			y=y/4
			cv2.putText(img,str(int(height))+" "+str(int(thing[9]*100)),(x,y), font, 1,(255,255,255),1,cv2.LINE_AA)
	
			cv2.polylines(img,thing[10],True,(255,0,0)) #Draw both squares
			tvecindex+=1
		if(tvecindex!=0):
			averageheight=averageheight/tvecindex
			heights[0]=[averageheight,scorethreshold/.95]
			cv2.putText(img,str(int(averageheight)),(30,30), font, 1,(255,255,255),1,cv2.LINE_AA)
		else:
			cv2.putText(img,"N/A",(30,30), font, 1,(255,255,255),1,cv2.LINE_AA)
	else:
		cv2.putText(img,"N/A",(30,30), font, 1,(255,255,255),1,cv2.LINE_AA)
	#print("") #Divider line
	weights=[.5,.3,.2]
	totalscore=weights[0]*heights[0][1]+weights[1]*heights[1][1]+weights[2]*heights[2][1]
	if(totalscore!=0):
		heights[0]=[(weights[0]*heights[0][1]*heights[0][0]+weights[1]*heights[1][1]*heights[1][0]+weights[2]*heights[2][1]*heights[2][0])/totalscore,totalscore]
		cv2.putText(img,str(int(heights[0][0])),(60,60), font, 1,(255,255,255),1,cv2.LINE_AA)
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
#cv2.destroyAllWindows() #And don't leave silly windows behind.
