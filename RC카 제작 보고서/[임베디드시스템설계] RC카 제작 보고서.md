# [임베디드시스템설계] RC카 제작 보고서

2018920002 고다현

2018920027 서인해



## 코드 설명

#### main.py

Image, Utils 모듈을 사용하는 메인 파일이다.

```python
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

```





#### Utils.py

카메라가 찍은 이미지를 처리하거나 진행 방향을 계산해서 serial.ino와 통신하는 파일이다.

아래와 같은 함수가 정의되어 있다.

- **SlicePart(im, images, slices)** : 이미지 im을 slices 수만큼 조각내서 images 배열에 담고 무게중심점들을 리턴하는 함수
- **RepackImages(images)** : images 배열에 있는 이미지들을 다시 합쳐 리턴하는 함수. 화면에 이미지를 출력해서 디버깅하기 위함.
- **Move(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10)** : images 배열에 있는 이미지들의 검정색 트랙의 중심점 x1, x2, ..., x10을 인자로 받아 RC카가 나아가야 할 방향을 계산하고 serial.ino 와 통신하는 함수

```python
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

    
```



#### Image.py

카메라가 찍은 이미지를 처리하는 파일이다.

아래와 같은 함수가 정의되어 있다.

- **Process(self)** : 이미지를 흑백, gaussian blur 처리한 뒤 무게중심점, 윤곽선을 얻고 무게중심점을 리턴하는 함수
- **getContourCenter(self, contour)** 
- **getContourExtent(self, contour)** 
- **correctMainContour(self, prev_cx)** 
- **Aprox(self, a, b, error)**

```python
import numpy as np
import cv2

class Image:
    
    def __init__(self):
        self.image = None
        self.contourCenterX = 0
        self.MainContour = None
        
    def Process(self):
	    # 이미지를 흑백으로 변환한 뒤 Threshold 값을 기준으로 0 또는 1로 값을 정한다
        imgray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) #Convert to Gray Scale
        self.contourCenterX = -1000

        # Gaussian blur
        blur = cv2.GaussianBlur(imgray,(5,5),0)
        ret, thresh = cv2.threshold(blur,100,255,cv2.THRESH_BINARY_INV) #Get Threshold
        self.contours, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 		  # Get contour
        self.prev_MC = self.MainContour

        self.height, self.width  = self.image.shape[:2]
        self.middleX = int(self.width/2) #Get X coordenate of the middle point
        self.middleY = int(self.height/2) #Get Y coordenate of the middle point
            

        if self.contours:
            self.MainContour = max(self.contours, key=cv2.contourArea)
            
            self.prev_cX = self.contourCenterX
            if self.getContourCenter(self.MainContour) != 0:
                self.contourCenterX = self.getContourCenter(self.MainContour)[0]
                if abs(self.prev_cX-self.contourCenterX) > 5:
                    self.correctMainContour(self.prev_cX)
            else:
                self.contourCenterX = 0
            
            self.dir =  int((self.middleX-self.contourCenterX) * self.getContourExtent(self.MainContour))
            
            #윤곽선은 초록색, 무게중심은 흰색 원, 그림의 중앙 지점은 빨간 원으로 표시
            cv2.drawContours(self.image,self.MainContour,-1,(0,255,0),3) #Draw Contour GREEN
            cv2.circle(self.image, (self.contourCenterX, self.middleY), 7, (255,255,255), -1) #Draw dX circle WHITE
            cv2.circle(self.image, (self.middleX, self.middleY), 3, (0,0,255), -1) #Draw middle circle RED

        return [self.contourCenterX, self.middleY]
	
    
    # 무게중심점을 구하는 함수
    def getContourCenter(self, contour):
        M = cv2.moments(contour)
        
        if M["m00"] == 0:
            return 0
        
        x = int(M["m10"]/M["m00"])
        y = int(M["m01"]/M["m00"])
        
        return [x,y]
    
    # 윤곽선 범위를 구하는 함수
    def getContourExtent(self, contour):
        area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        rect_area = w*h
        if rect_area > 0:
            return (float(area)/rect_area)
     
    def Aprox(self, a, b, error):
        if abs(a - b) < error:
            return True
        else:
            return False
            
    def correctMainContour(self, prev_cx):
        if abs(prev_cx-self.contourCenterX) > 5:
            for i in range(len(self.contours)):
                if self.getContourCenter(self.contours[i]) != 0:
                    tmp_cx = self.getContourCenter(self.contours[i])[0]
                    if self.Aprox(tmp_cx, prev_cx, 5) == True:
                        self.MainContour = self.contours[i]
                        if self.getContourCenter(self.MainContour) != 0:
                            self.contourCenterX = self.getContourCenter(self.MainContour)[0]
                            
```



#### serial.ino

main.py로부터 받아온 direction에 따라 모터의 속도를 제어하는 파일이다. 

```c
int motorA1 = 5;
int motorA2 = 6;
int motorB1 = 9;
int motorB2 = 10;
int speed = 255;

// initial command
int command = 0;

// main.py로부터 받아온 direction이 유효한 값인지 확인하는 함수
bool is_valid_direction(char direction)
{
  switch (direction)
  {
    case 'T': case 'l': case 'L': case 'r': case 'R': case 'B':
      return true;
  }

  return false;
}

void setup()
{
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  Serial.begin(9600);

  while (!Serial);

  Serial.println("Mars 2020");
}

void loop()
{
  if (Serial.available())
  {
    char direction;

    do
    {
      direction = Serial.read();
    }
    while (!is_valid_direction(direction));

    switch (direction)
    {
      //forward
      case 'T':
        analogWrite(motorA1, speed);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, speed);
        analogWrite(motorB2, 0);
        break;

      //left
      case 'l' :
        analogWrite(motorA1, 50);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, speed);
        analogWrite(motorB2, 0);
        break;

      //strong left
      case 'L':
        analogWrite(motorA1, 0);
        analogWrite(motorA2, 200);
        analogWrite(motorB1, speed);
        analogWrite(motorB2, 0);
        break;

      //right
      case 'r':
        analogWrite(motorA1, speed);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, 50);
        analogWrite(motorB2, 0);
        break;

      //strong right
      case 'R':
        analogWrite(motorA1, speed);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, 0);
        analogWrite(motorB2, 200);
        break;

      //back
      case 'B' :
        analogWrite(motorA1, 0);
        analogWrite(motorA2, speed);
        analogWrite(motorB1, 0);
        analogWrite(motorB2, speed);
        break;
    }
    if(direction == 'R' || direction == 'L'){
      delay(20);
    }
    if(direction == 'B'){
      delay(100);
    }
    else{
      delay(60);
    }
    analogWrite(motorA1, 0);
    analogWrite(motorA2, 0);
    analogWrite(motorB1, 0);
    analogWrite(motorB2, 0);
    //main.py에게 ACK 전송
    Serial.write("ACK\n");
    delay(50);
  }
}
```



## 주요 설계 원리

* picamera로 부터 받아오는 이미지를 가로로 10등분하여 조각냄

* 10등분한 이미지들에 인식된 트랙의 윤곽선과 무게 중심점을 구함
  * 트랙의 윤곽선들의 무게 중심점이 없다면 후진하도록 값을 설정
  * 어떠한 오류로 인해 잘못된 윤곽선이 인식될 경우를 대비하여, 화면의 가장자리에서부터 각각 Margin(: 10으로 설정)보다 적게 떨어져 있다면 그 무게 중심점은 유효하지 않도록 설정
* 무게 중심점들의 x좌표들의 평균(valid_xs_avg)과 무게 중심점들의 x좌표들의 각 간격마다의 차이값의 평균(dif_avg)을 더한 값을 이용해 방향을 선택
  * 무게 중심점들의 x좌표들의 평균은 0~320 사이를 가짐
  * 무게 중심점들의 x좌표들의 각 간격마다의 차이값의 평균은 대부분 -50~50 사이의 값을 가짐
  * 값의 범위가 다른 두 개의 수치를 더함으로써 무게중심점들의 x좌표들의 평균을 무게중심점들의 x좌표의 차이값보다 더 큰 가중치를 부여
    * 다양한 가중치를 두어 설정해보았지만, 단순히 더한 값으로 하는 것이 가장 깔끔한 결과를 얻어냄
* (최고)속도는 255로 설정
* 방향
  * 직진
    * 두 바퀴 모두 최고속도로 직진
    * 0.06 초 동안 작동
  * 좌회전
    * 오른쪽 바퀴는 최고속도로 직진 / 왼쪽바퀴는 속도 50으로 작동
    * 0.06 초 동안 작동
  * 강한 좌회전
    * 오른쪽 바퀴는 최고속도로 직진 / 왼쪽 바퀴는 최고속도로 후진
    * 0.02 초 동안 작동
  * 우회전
    * 왼쪽 바퀴는 최고속도로 직진 / 오른쪽바퀴는 속도 50으로 작동
    * 0.06 초 동안 작동
  * 강한 우회전
    * 왼쪽 바퀴는 최고속도로 직진 / 오른쪽 바퀴는 최고속도로 후진
    * 0.02 초 동안 작동
  * 후진
    * 두 바퀴 모두 최고속도로 후진
    * 0.1 초 동안 작동
* 라즈베리파이가 아두이노에 방향값을 보낸 후(send 메세지 전송) 아두이노가 라즈베리파이에 이에 대한 ACK를 보내야 라즈베리파이가 다음 방향값을 보낼 수 있도록 함
* 라즈베리파이 부팅 시, 코드가 바로 실행되도록 설정



## 오차 보정

* RC카에서 가까운 7개의 이미지만 고려(: zoom 시키는 것과 같은 역할) 
  * picamera가 차체와 조금 떨어진 곳을 비추는 점을 보완
  * RC카가 직각 코너에서 필요 이상으로 일찍 턴하는 문제를 해결
* 무게중심점들이  모두 한쪽으로 치우쳐졌을 때의 오차를 보정
  * 왼쪽으로 치우쳐져 있다면, 범위에 따라 x좌표들의 차이값의 평균을 -20, -50으로 조정
  * 오른쪽으로 치우쳐져 있다면, 범위에 따라 x좌표들의 차이값의 평균을 20, 50으로 조정

* 해상도를 낮추어서 라즈베리파이가 코드를 읽어들이는 속도를 보정

* 밝기와 대비를 조정하여 그림자를 보정함으로써 트랙을 정확히 인식하도록함

  * 밝기와 대비를 극단적으로 높였을 때, 트랙까지 인식하지 못하는 경우가 발생하여 적절한 수를 대입

* 차체와 모터 사이의 간격이 있어 헐거워짐을 방지하기 위해 사이에 종이를 끼워넣음

  <img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209092618159.png" alt="image-20201209092618159" style="zoom:7%;" />

* 아두이노와 라즈베리를 연결하는 선이 picamera의 화면에 나와서 절연테이프를 이용해 나오지 않도록 조정

<img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209092733339.png" alt="image-20201209092733339" style="zoom:7%;" />

* picamera가 한쪽으로 기울어지는 것을 방지하기 위해 병뚜껑으로 받쳐줌으로써 올바른 시야를 확보할 수 있도록함

  <img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209092917659.png" alt="image-20201209092917659" style="zoom:7%;" />

## 과정 사진

* 직접 트랙을 만들어 시연해보는 과정을 반복하여 계속적으로 코드 수정

  <img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209093008882.png" alt="image-20201209093008882" style="zoom: 7%;" /> <img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209093412850.png" alt="image-20201209093412850" style="zoom:7%;" />

  

* 정기관 2층에 배치된 연습용 트랙을 이용하여 시행해봄

<img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209093113929.png" alt="image-20201209093113929" style="zoom:9%;" /> <img src="C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20201209093139960.png" alt="image-20201209093139960" style="zoom:7.5%;" />