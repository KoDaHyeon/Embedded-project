# -*- coding: utf-8 -*-

import numpy as np
import cv2
import time
from Image import *
import serial

WIDTH = 320
MARGIN = 10

ser = serial.Serial("/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_754393137373514101B0-if00", 9600)

# 그림을 slices 의 수만큼 조각낸다
def SlicePart(im, images, slices):
    height, width = im.shape[:2]
    sl = int(height/slices)
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
  xs = [x4, x5, x6, x7, x8, x9, x10] # all points
  valid_xs = []                                  # all valid points
  dif_xs = []                                    # all differents
  sum = 0                                        # sum of differents
  dif_avg = 0                                    # average of differents
  valid_xs_avg = 0
  result = 0

  # populate only valid points
  for i in xs:
    if i >= WIDTH - MARGIN or i <= MARGIN:
      continue
    valid_xs.append(i)
    valid_xs_avg += i

  # not enough valid points
  if len(valid_xs) == 0:
    dif_avg = 1000
  # calculate different between every point
  else:
    valid_xs_avg /= len(valid_xs)
    print(valid_xs)
    print(valid_xs_avg)
    if valid_xs_avg > 0 and valid_xs_avg <= 40:
      for now in valid_xs:
        dif_xs.append(-50)
    elif valid_xs_avg > 40 and valid_xs_avg <= 80:
      for now in valid_xs:
        dif_xs.append(-20)
    elif valid_xs_avg > 280 and valid_xs_avg <= 320:
       for now in valid_xs:
        dif_xs.append(50)
    elif valid_xs_avg > 240 and valid_xs_avg <= 280:
      for now in valid_xs:
        dif_xs.append(20)
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

  
  result = valid_xs_avg + dif_avg
  
  print(str(valid_xs_avg) + '\n')
  print(str(dif_avg) +'\n')
  print(str(result) + '\n')
  
  
  # make a command

  #forward
  if result >= 100 and result < 230:
    print("On Track!!!! Keep going~~~!!!>__<")
    direction = 'T'
    
  #left  
  elif result >= 50 and result < 100:
    print("Turn Left!!@__@")
    direction = 'l'
  
  #strong left
  elif result < 50:
    print("Turn Left!!!!!!!!!!!!!!@__@")
    direction = 'L'
    
  #right
  elif result >= 230 and result < 300:
    print("Turn Right!!^3^")
    direction = 'r'
      
  #strong right
  elif result >= 300 and result <1000:
    print("Turn Right!!!!!!!!!!!!^ 3^")
    direction = 'R'
      
  #back
  else:
    print("Backkkkkkkkkkk!^&*%*%!&@^(&#!@_&@!*@%*%")
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
    

