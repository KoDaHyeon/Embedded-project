# -*- coding: utf-8 -*-
# 이 코드는 gunhoflash와 완전 똑같음~~
import numpy as np
import cv2
import time
from Image import *
import serial

WIDTH = 320
MARGIN = 10

ser = serial.Serial("/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_754393137373514101B0-if00", 9600)
if ser is None:
  ser = serial.Serial("/dev/ttyACM1", 9600)

# 그림을 slices 의 수만큼 조각낸다
def SlicePart(im, images, slices):
    height, width = im.shape[:2]
    sl = int(height/slices);
    points = []

    for i in range(slices):
        part = sl*i
        crop_img = im[part:part+sl, 0:width]
        #조각난 이미지 crop_img를 images[]에 저장
        images[i].image = crop_img
        #Image.py에서 윤곽선을 그리고 무게중심을 표시
        cPoint = images[i].Process()
        points.append(cPoint)
    return points

#조각난 이미지를 다시 합친다
def RepackImages(images):
    img = images[0].image
    for i in range(len(images)):
        if i == 0:
            img = np.concatenate((img, images[1].image), axis=0)
        if i > 1:
            img = np.concatenate((img, images[i].image), axis=0)
            
    return img

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
  if len(valid_xs) == 0:
    dif_avg = 1000
  # calculate different between every point
  else:
    prev = valid_xs[0]
    for now in valid_xs:        
      if now != valid_xs[0]:
        dif = prev - now
        dif_xs.append(dif)
        prev = now

  
  # calculate sum and average
  for j in dif_xs:
    sum += j
  
  if len(dif_xs) == 0:
    dif_avg = 1000
  else:
    dif_avg = sum / len(dif_xs)

  print(dif_xs)
  print(str(sum) + '\n')
  print(str(dif_avg) + '\n')
  
  # make a command

  # 직진
  if dif_avg <= 6 and dif_avg >= -6:
    print("On Track! Keep going!! GOGOGO")
    direction = 'T'

  # 좌회전
  elif dif_avg < -6 and dif_avg >= -30:
    print("Turn Left!")
    direction = 'l'

  # 더 격한 좌회전
  elif dif_avg < -30:
    print("Turn Left!!!!!!!!!꺅!!!")
    direction = 'L'

  # 우회전
  elif dif_avg > 6 and dif_avg <= 30:
    print("Turn Right!")
    direction = 'r'

  # 더 격한 우회전
  elif dif_avg > 30 and dif_avg < 1000:
    print("Turn Right!!!!!!!!홋!")
    direction = 'R'

  # 후진
  else: 
    print("Back!")
    direction = 'B'
  
  # cmd = ("%c\n" % (direction)).encode('ascii')
  ser.write(direction.encode())
  print("send")
  read_serial = ser.readline()
  print("<<< %s" % (read_serial))

def Center(moments):
    if moments["m00"] == 0:
        return 0
        
    x = int(moments["m10"]/moments["m00"])
    y = int(moments["m01"]/moments["m00"])

    return x, y
    
def RemoveBackground(image, b):
    up = 100
    # create NumPy arrays from the boundaries
    lower = np.array([0, 0, 0], dtype = "uint8")
    upper = np.array([up, up, up], dtype = "uint8")
    #----------------COLOR SELECTION-------------- (Remove any area that is whiter than 'upper')
    if b == True:
        mask = cv2.inRange(image, lower, upper)
        image = cv2.bitwise_and(image, image, mask = mask)
        image = cv2.bitwise_not(image, image, mask = mask)
        image = (255-image)
        return image
    else:
        return image
    #////////////////COLOR SELECTION/////////////
    

