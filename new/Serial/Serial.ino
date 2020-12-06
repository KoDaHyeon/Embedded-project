int motorA1 =  5; 
int motorA2  = 6; 
int motorB1 =  9; 
int motorB2 =  10; 
int speed = 170;

// initial command
int command = 0;

void setup()

{
  pinMode( motorA1 , OUTPUT); 
  pinMode( motorA2 , OUTPUT); 
  pinMode( motorB1 , OUTPUT); 
  pinMode( motorB2 , OUTPUT);
  Serial.begin(9600);
  
  while (!Serial);
  
  Serial.println("OpenCV 3SU CAR");

}

void loop() {

if (Serial.available())

{
  //int state = Serial.parseInt();
  char direction = Serial.read();

  if (direction == 'T')
  {
    analogWrite( motorA1 , speed); 
    analogWrite( motorA2 , 0); 
    analogWrite( motorB1 , speed); 
    analogWrite( motorB2 , 0);
    Serial.println("On Track! Keep going!! GOGOGO");
  }

   if (direction == 'l')
  {
  
    analogWrite( motorA1 , speed);
    analogWrite( motorA2 , 0);
    analogWrite( motorB1 , 0);
    analogWrite( motorB2 , 0);
    Serial.println("Turn Left!");
  }

   if (direction == 'L')
  {
  
    analogWrite( motorA1 , speed);
    analogWrite( motorA2 , 0);
    analogWrite( motorB1 , 0);
    analogWrite( motorB2 , 100);
    Serial.println("Turn Left!!!!!!!!!");
  }

   if (direction == 'r')
  {
  
    analogWrite( motorA1 , 0);
    analogWrite( motorA2 , 0);
    analogWrite( motorB1 , speed);
    analogWrite( motorB2 , 0);
    Serial.println("Turn Right!");
  }

  if (direction == 'R')
  {
    analogWrite( motorA1 , 0);
    analogWrite( motorA2 , 100);
    analogWrite( motorB1 , speed);
    analogWrite( motorB2 , 0);
    Serial.println("Turn Right!!!!!!!");
  }

  if (direction == 'B')
  {
    analogWrite( motorA1 , 0);
    analogWrite( motorA2 , 100);
    analogWrite( motorB1 , 0);
    analogWrite( motorB2 , 100);
    Serial.println("Back!");
  }

}

}
