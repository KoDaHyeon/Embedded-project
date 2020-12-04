# -*- coding: utf-8 -*-
# 이 코드는 gunhoflash와 완전 똑같음~~
import numpy as np
import cv2
import time
from Image import *

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