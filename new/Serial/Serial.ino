int motorA1 = 5;
int motorA2 = 6;
int motorB1 = 9;
int motorB2 = 10;
int speed = 255;

// initial command
int command = 0;

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
    //int state = Serial.parseInt();
    char direction;

    do
    {
      direction = Serial.read();
    }
    while (!is_valid_direction(direction));

    switch (direction)
    {
      case 'T':
        analogWrite(motorA1, speed);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, speed);
        analogWrite(motorB2, 0);
        //Serial.println("On Track! Keep going!! GOGOGO");
        break;

      case 'l' :
        analogWrite(motorA1, 50);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, speed);
        analogWrite(motorB2, 0);
        //Serial.println("Turn Left!");
        break;

      case 'L':
        analogWrite(motorA1, 0);
        analogWrite(motorA2, speed);
        analogWrite(motorB1, speed);
        analogWrite(motorB2, 0);
        //Serial.println("Turn Left!!!!!!!!!");
        break;

      case 'r':
        analogWrite(motorA1, speed);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, 50);
        analogWrite(motorB2, 0);
        //Serial.println("Turn Right!");
        break;

      case 'R':
        analogWrite(motorA1, speed);
        analogWrite(motorA2, 0);
        analogWrite(motorB1, 0);
        analogWrite(motorB2, speed);
        //Serial.println("Turn Right!!!!!!!");
        break;

      case 'B' :
        analogWrite(motorA1, 0);
        analogWrite(motorA2, speed);
        analogWrite(motorB1, 0);
        analogWrite(motorB2, speed);
        //Serial.println("Back!");
        break;
    }

    delay(150);
    analogWrite(motorA1, 0);
    analogWrite(motorA2, 0);
    analogWrite(motorB1, 0);
    analogWrite(motorB2, 0);
    Serial.write("ACK\n");
  }
}
