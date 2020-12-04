import socket
import sys
import os
import numpy as np
import pdb
import serial
import picamera

import cv2
import time

from Image import *
from Utils import *

font = cv2.FONT_HERSHEY_SIMPLEX
direction = 0

TOLERANCE = 145
TURN_MAX = 190
TURN_MID = 90
WIDTH = 320
HEIGHT = 240

#N_SLICES만큼 이미지를 조각내서 Images[] 배열에 담는다
Images=[]
N_SLICES = 6

ser = serial.Serial('/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_754393137373514101B0-if00', 9600)
if ser is None:
  ser = serial.Serial('/dev/ttyUSB1', 9600)

print('start')
time.sleep(3)

for q in range(N_SLICES):
  Images.append(Image())


def in_tolerance(n):
  if n < -TOLERANCE:
    return False
  if n > TOLERANCE:
    return False
  return True

def get_cmd(y1, y2, y3, y4, y5, y6):

  num_valid = 3
  
  y1 -= WIDTH/2
  y2 -= WIDTH/2
  y3 -= WIDTH/2
  y4 -= WIDTH/2
  y5 -= WIDTH/2
  y6 -= WIDTH/2
  
  master_point = 0
  
  # +: right
  # -: left
  if in_tolerance(y1) == False:
      num_valid -= 1
      y1 = 0
  if in_tolerance(y2) == False:
      num_valid -= 1
      y2 = 0
  if in_tolerance(y3) == False:
      num_valid -= 1
      y3 = 0
  if in_tolerance(y4) == False:
      num_valid -= 1
      y4 = 0
  if in_tolerance(y5) == False:
      num_valid -= 1
      y5 = 0
  if in_tolerance(y6) == False:
      num_valid -= 1
      y6 = 0

  
  master_point = 2.65 * (y1 * 0.7 + y2 * 0.85 + y3 + y4 * 1.1 + y5 * 1.2 + y6 * 1.35) / (num_valid + 0.1)

  master_point += y1 * 0.5
  master_point += y2 * 0.4
  master_point += y3 * 0.3
  master_point -= y4 * 0.4
  master_point -= y5 * 0.5
  master_point -= y6 * 0.6

  # back
  if num_valid < 2:
      direction = 'B'
  else:
      direction = 'G'
      if master_point > TURN_MID and master_point < TURN_MAX :
          direction = 'l'
      if master_point < -TURN_MID and master_point > -TURN_MAX :
          direction = 'r'
      if master_point >= TURN_MAX :
          direction = 'L'
      if master_point <= -TURN_MAX :
          direction = 'R'

  cmd = ("%c\n" % (direction)).encode('ascii')

  print(">>> master_point:%d, cmd:%s" % (master_point, cmd))
  
  ser.write(cmd)
  print("send")
  # read cmd from arduino and print it    
  read_serial = ser.readline()
  print("<<< %s" % (read_serial))


#사진 찍기
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = picamera.array.PiRGBArray(camera, size = (640, 480))
time.sleep(0.1)

#루프
for frame in camera.capture_continuous (rawCapture, format = "bgr", use_video_port = True):
  image = frame.array
  #image = cv2.imread('C:\Users\aasai\Desktop\out.jpg')
  image = cv2.resize(image,(500,300))
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray,(5,5),0)

  #color thresholding
  ret,thresh = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)

  if skip > 0 :
    skip -= 1
  elif blur is not None:
    skip = 6

    #이미지를 조각내서 윤곽선을 표시하게 무게중심 점을 얻는다
    Points = SlicePart(blur, Images, N_SLICES)
    print('Points : ', Points)

    #N_SLICES 개의 무게중심 점을 x좌표, y좌표끼리 나눈다
    #x = Points[::2]
    #y = Points[1::2]


    #조각난 이미지를 한 개로 합친다(디버깅용)
    fm = RepackImages(Images)
    
    #완성된 이미지를 표시한다(디버깅용)
    cv2.imshow("Vision Race", fm)
    rawCapture.truncate(0)
    if cv2.waitKey(0) & 0xFF == ord('q'):
      cv2.destroyAllWindows()

    #command
    get_cmd(Points[0][0], Points[1][0], Points[2][0], Points[3][0], Points[4][0], Points[5][0])
    
  else:
    print('not even processed')
    
