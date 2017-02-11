import numpy as np
import cv2
import os

camera=cv2.VideoCapture(1)
write=False
nums=0
os.chdir("ChessBoardPics")
while True:
	ret, image=camera.read()
	image2=np.copy(image)
	ret,corners=cv2.findChessboardCorners(image2,(9,6))
	if(ret):
		cv2.drawChessboardCorners(image2,(9, 6),corners,ret)
	cv2.imshow("Arbitrarily named Webcam",image2)
	key=cv2.waitKey(1)
	if key==27:
		break
	if key==32:
		cv2.imwrite("Board"+str(nums)+".png",image)
		nums+=1
cam.release()
cv2.destroyAllWindows()
