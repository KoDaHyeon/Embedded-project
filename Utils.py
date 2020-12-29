import numpy as np
import cv2
import time
from Image import *
import serial

WIDTH = 320
MARGIN = 10

ser = serial.Serial("/dev/serial/by-id/usb-Arduino_Srl_Arduino_Uno_754393137373514101B0-if00", 9600)

# 이미지(im)를 slices 수만큼 조각내서 images 배열에 담는 함수
def SlicePart(im, images, slices):
    height, width = im.shape[:2]
    sl = int(height/slices)
    points = []

    for i in range(slices):
        part = sl*i
        crop_img = im[part:part+sl, 0:width]
        # 조각난 이미지 crop_img를 images[]에 저장
        images[i].image = crop_img
        # Image.py에서 윤곽선을 그리고 무게중심을 표시
        cPoint = images[i].Process()
        points.append(cPoint)
    # 무게중심점들을 리턴
    return points

# images 배열에 있는 이미지들을 다시 합쳐 리턴하는 함수
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
  xs = [x4, x5, x6, x7, x8, x9, x10] # RC카에서 가까운 부분을 중점적으로 고려
  valid_xs = []  # 일정 범위 이내의 점들
  dif_xs = [] # valid_xs 간의 차이값
  sum = 0  # dif_xs 들의 합
  dif_avg = 0  # dif_xs들의 평균
  valid_xs_avg = 0 # valid_xs들의 평균
  result = 0 # valid_xs_avg, dif_avg를 일정 비율로 더한 값

  # 일정 범위 이내의 점만 고려함
  for i in xs:
    if i >= WIDTH - MARGIN or i <= MARGIN:
      continue
    valid_xs.append(i)
    valid_xs_avg += i

  # 일정 범위 이내의 점이 하나도 없는 경우, dif_avg 값을 1000으로 줘서 back하도록 함
  if len(valid_xs) == 0:
    dif_avg = 1000
    
  # 일정 범위 이내의 점들(valid_xs)간의 차이를 계산
  else:
    valid_xs_avg /= len(valid_xs)
    
    # valid_xs들이 모두 한쪽으로 치우쳐졌을 때 오차 보정
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
     
  # dif_xs들의 합(sum), 평균(dif_avg)을 계산
  for j in dif_xs:
    sum += j
  
  if len(dif_xs) == 0:
    dif_avg = 1000
  else:
    dif_avg = sum / len(dif_xs)


  result = valid_xs_avg + dif_avg
  
  # for debugging
  print(str(valid_xs_avg) + '\n')
  print(str(dif_avg) +'\n')
  print(str(result) + '\n')
  
  
  # make a command

  #forward
  if result >= 100 and result <230:
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
  elif result >=230 and result <300:
    print("Turn Right!!^3^")
    direction = 'r'
      
  #strong right
  elif result >=300 and result <1000:
    print("Turn Right!!!!!!!!!!!!^ 3^")
    direction = 'R'
      
  #back
  else:
    print("Backkkkkkkkkkk!^&*%*%!&@^(&#!@_&@!*@%*%")
    direction = 'B'

  # serial.ino에 direction값을 전송
  ser.write(direction.encode())
  print("send")

  # serial.ino에서 ACK를 수신
  read_serial = ser.readline()
  print("<<< %s" % (read_serial))
