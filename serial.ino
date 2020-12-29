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
