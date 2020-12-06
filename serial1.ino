int motorA1 =  5; 
int motorA2  = 6; 
int motorB1 =  9; 
int motorB2 =  10; 
int  speed = 170;

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
  int state = Serial.read();

  if (state == 3)
  {
    
    analogWrite( motorA1 , 150); 
    analogWrite( motorA2 , 0); 
    analogWrite( motorB1 , 150); 
    analogWrite( motorB2 , 0);
    Serial.println("Go Straight!");
  }

  if (state == 2)
  {
    analogWrite( motorA1 , 0);
    analogWrite( motorA2 , speed);
    analogWrite( motorB1 , 0);
    analogWrite( motorB2 , speed);
    Serial.println("Reverse");
  }

  if (state == 4)
  {
  
    analogWrite( motorA1 , speed);
    analogWrite( motorA2 , 0);
    analogWrite( motorB1 , 0);
    analogWrite( motorB2 , speed);
    Serial.println("Turn Left!");
  }
  if (state == 1)
  {
  analogWrite( motorA1 , 0);
  analogWrite( motorA2 , speed);
  analogWrite( motorB1 , speed);
  analogWrite( motorB2 , 0);
Serial.println("Turn Right!");
  }
  if (state == 5)
  {
  
  digitalWrite( motorA1 , 0);
  digitalWrite( motorA2 , 0);
  digitalWrite( motorB1 , 0);
  digitalWrite( motorB2 , 0);

  Serial.println("Stop");
  }

}

}

