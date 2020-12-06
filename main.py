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
WIDTH = 320
MARGIN = 10

direction = ''

print('start')
time.sleep(3)

ser = serial.Serial("/dev/ttyACM0", 9600)
if ser is None:
  ser = serial.Serial("/dev/ttyACM1", 9600)

for q in range(N_SLICES):
  Images.append(Image())

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
zf = 0.2
camera.zoom = (0+zf, 0+zf, 1-2*zf, 1-2*zf)
rawCapture = picamera.array.PiRGBArray(camera, size = (640, 480))
time.sleep (0.1)

for frame in camera.capture_continuous (rawCapture, format = "bgr", use_video_port = True):
    image = frame.array
    image = cv2.resize(image,(320,240))
    # Convert to grayscale
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Gussian blur
    blurred = cv2.GaussianBlur(imgray, (5, 5), 0)

    # Color thresholding
    ret,thresh = cv2.threshold(blurred,60,255,cv2.THRESH_BINARY_INV)

    # 이미지를 조각내서 윤곽선을 표시하게 무게중심 점을 얻는다
    Points = SlicePart(thresh.copy(), Images, N_SLICES)
    print('Points : ', Points)

    # 조각난 이미지를 한 개로 합친다
    fm = RepackImages(Images)


    # 진행 방향 계산
    def Move(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10):
      xs = [x1, x2, x3, x4, x5, x6, x7, x8, x9, x10] # all points
      valid_xs = []                                  # all valid points
      dif_xs = []                                    # all differents
      sum = 0                                        # sum of differents
      dif_avg = 0                                    # average of differents

      # populate only valid points
      for i in xs:
        if i >= WIDTH - MARGIN or i <= MARGIN:
          continue
        valid_xs.append(i)

      # TODO: handle exception: not enough valid points
      
      # calculate different between every point
      prev = valid_xs[0]
      for now in valid_xs:        
        if now != valid_xs[0]:
          dif = now - prev
          dif_xs.append(dif)
          prev = now
      
      # calculate sum and average
      for j in dif_xs:
        sum += j
      dif_avg = sum / len(dif_xs)

      # make a command

      # 직진
      if dif_avg >= 10 or dif_avg <= -10:
        print("On Track! Keep going!! GOGOGO")
        direction = 'T'

      # 좌회전
      elif dif_avg < -10 or dif_avg >= -30:
        print("Turn Left!")
        direction = 'l'

      # 더 격한 좌회전
      elif dif_avg < -30:
        print("Turn Left!!!!!!!!!꺅!!!")
        direction = 'L'

      # 우회전
      elif dif_avg > 10 or dif_avg <= 30:
        print("Turn Right!")
        direction = 'r'

      # 더 격한 우회전
      elif dif_avg > 30:
        print("Turn Right!!!!!!!!홋!")
        direction = 'R'

      # 후진
      else: 
        print("Back!")
        direction = 'B'
      
      # cmd = ("%c\n" % (direction)).encode('ascii')
      ser.write(direction.encode())
      
    '''
    # Find the contours of the frame
    contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

    # Find the biggest contour (if detected)
    
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        cv2.line(image,(cx,0),(cx,720),(255,0,0),1)
        cv2.line(image,(0,cy),(1280,cy),(255,0,0),1)
        cv2.drawContours(image, contours, -1, (0,255,0), 1)

        print (cx)
        print (cy)

        # 좌회전
        if cx >= 1100:
          ser.write(chr(4).encode())
          print ("Turn Left!")
        # 직진
        if cx < 1100 and cx > 800:
          ser.write(chr(3).encode())
          print ("On Track!")
        # 우회전
        if cx <= 800:
          ser.write(chr(1).encode())
          print ("Turn Right!")
    # 후진
    else:
      ser.write(chr(2).encode())
      print("Reverse")
'''

    #Display the resulting frame
    cv2.imshow('frame', fm)
    rawCapture.truncate(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      print("Stopped!")
      break

# Closes all the frames
cv2.destroyAllWindows()