from Image import *
from Utils import *

import cv2
import numpy as np
import pdb
import serial
import picamera
import picamera.array
import time

# N_SLICES만큼 이미지를 조각내서 Images[]배열에 담음
Images = []
N_SLICES = 10

direction = ''

print('start')
time.sleep(3)

for q in range(N_SLICES):
  Images.append(Image())

camera = picamera.PiCamera()
camera.resolution = (320, 240) # 해상도
camera.framerate = 30
camera.brightness = 60 # 밝기 : 기본값은 50. 그림자를 제거하기 위해 밝기를 높임
camera.contrast = 65 # 대비 : 기본값은 50. 그림자를 제거하기 위해 대비를 높임

# 이미지의 중간 부분을 크롭해서 digital zoom
zf = 0.2
camera.zoom = (0+zf, 0+zf, 1-2*zf, 1-2*zf)
rawCapture = picamera.array.PiRGBArray(camera, size = (320, 240))
time.sleep (0.1)


for frame in camera.capture_continuous (rawCapture, format = "bgr", use_video_port = True):
    image = frame.array
    image = cv2.resize(image,(320,240))

    # 이미지를 조각내서 윤곽선을 표시하고 무게중심 점을 얻음
    Points = SlicePart(image, Images, N_SLICES)

    # 조각난 이미지를 한 개로 합침
    fm = RepackImages(Images)

	# 진행 방향을 계산해서 serial.ino 에 direction을 보냄
    Move(Points[0][0], Points[1][0], Points[2][0], Points[3][0], Points[4][0], Points[5][0], Points[6][0], Points[7][0], Points[8][0], Points[9][0])
    
    # 이미지를 화면에 출력
    cv2.imshow('frame', fm)
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      print("Stopped!")
      break

	
# Closes all the frames
cv2.destroyAllWindows()
