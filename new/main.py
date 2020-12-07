from Image import *
from Utils import *

import cv2
import numpy as np
import pdb
import serial
import picamera
import picamera.array
import time


#N_SLICES만큼 이미지를 조각내서 Images[]배열에 담는다
Images = []
N_SLICES = 10


direction = ''

print('start')
time.sleep(3)



for q in range(N_SLICES):
  Images.append(Image())

camera = picamera.PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
zf = 0.2
camera.zoom = (0+zf, 0+zf, 1-2*zf, 1-2*zf)
rawCapture = picamera.array.PiRGBArray(camera, size = (320, 240))
time.sleep (0.1)


for frame in camera.capture_continuous (rawCapture, format = "bgr", use_video_port = True):
    # time.sleep(0.1)
    image = frame.array
    image = cv2.resize(image,(320,240))

    # 이미지를 조각내서 윤곽선을 표시하게 무게중심 점을 얻는다
    Points = SlicePart(image, Images, N_SLICES)
    #print('Points : ', Points)

    # 조각난 이미지를 한 개로 합친다
    fm = RepackImages(Images)


    Move(Points[0][0], Points[1][0], Points[2][0], Points[3][0], Points[4][0], Points[5][0], Points[6][0], Points[7][0], Points[8][0], Points[9][0])
    #Display the resulting frame
    cv2.imshow('frame', fm)
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      print("Stopped!")
      break

# Closes all the frames
cv2.destroyAllWindows()
