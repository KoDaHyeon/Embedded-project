#include <AFMotor.h>
#define R_MAX 230
#define L_MAX 255

// Motor L293D 3:M3, 4:M4
AF_DCMotor motor_L(3);
AF_DCMotor motor_R(4);

void cmd() {
  byte DataToRead[2];
  DataToRead[1] = '\n';
  Serial.readBytesUntil(char(13), DataToRead, 2);

  char direction_type = DataToRead[0]; // L R l r G B
  int i = 1;
  while (DataToRead[i] != '\n' && i < 2) i++;

  switch (direction_type) {
    case 'L':
      motor_L.setSpeed(L_MAX);
      motor_R.setSpeed(R_MAX);
      motor_L.run(RELEASE);
      motor_R.run(FORWARD);
      delay(210);
      break;
    case 'R':
      motor_L.setSpeed(L_MAX);
      motor_R.setSpeed(R_MAX);
      motor_L.run(FORWARD);
      motor_R.run(RELEASE);
      delay(210);
      break;
    case 'l':
      motor_L.setSpeed(L_MAX);
      motor_R.setSpeed(R_MAX);
      motor_L.run(RELEASE);
      motor_R.run(FORWARD);
      delay(130);
      break;
    case 'r':
      motor_L.setSpeed(L_MAX);
      motor_R.setSpeed(R_MAX);
      motor_L.run(FORWARD);
      motor_R.run(RELEASE);
      delay(130);
      break;
    case 'G':
      motor_L.setSpeed(L_MAX);
      motor_R.setSpeed(R_MAX);
      motor_L.run(FORWARD);
      motor_R.run(FORWARD);
      delay(400);
      break;
    case 'B':
      motor_L.setSpeed(L_MAX);
      motor_R.setSpeed(R_MAX);
      motor_L.run(BACKWARD);
      motor_R.run(BACKWARD);
      delay(300);
      break;
    default:
      motor_L.run(RELEASE);
      motor_R.run(RELEASE);
      Serial.write("ACK\n");
      return;
  }
  
  // For Debugging, send string to RPi
  delay(100);
  motor_L.run(RELEASE);
  motor_R.run(RELEASE);
  Serial.write("ACK\n");
}

void setup() {
  Serial.begin(9600);
  
  motor_L.setSpeed(L_MAX);
  motor_R.setSpeed(R_MAX);
  motor_L.run(RELEASE);
  motor_R.run(RELEASE);
}

void test() {
  motor_L.setSpeed(L_MAX);
  motor_R.setSpeed(R_MAX);
  motor_L.run(FORWARD);
  motor_R.run(FORWARD);
  delay(2000);
}

void loop() {
  /*while (1) {
    test();
  }*/
  cmd();
}
