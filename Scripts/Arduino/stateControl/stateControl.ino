#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"


#define PIN 6
#define NUM_LEDS 7
uint8_t BRIGHTNESS = 50;
int gamma[] = {
  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
  1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
  2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
  5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
  10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
  17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
  25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
  37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
  51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
  69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
  90, 92, 93, 95, 96, 98, 99, 101, 102, 104, 105, 107, 109, 110, 112, 114,
  115, 117, 119, 120, 122, 124, 126, 127, 129, 131, 133, 135, 137, 138, 140, 142,
  144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 167, 169, 171, 173, 175,
  177, 180, 182, 184, 186, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213,
  215, 218, 220, 223, 225, 228, 231, 233, 236, 239, 241, 244, 247, 249, 252, 255
};

int takeupPotTrigger = 900;
int takeupPotKiller = 950;
int feedPotTrigger = 755;
int feedPotKiller = 675;
bool takeupDCMotorRunning = false;
bool feedDCMotorRunning = false;

// the possible states of the state-machine
typedef enum {  NONE, GOT_L, GOT_S, GOT_X } states;

// current state-machine state
states state = NONE;
// current partial number
unsigned int currentValue;

Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *myStepper = AFMS.getStepper(200, 1);
Adafruit_DCMotor *takeupDCMotor = AFMS.getMotor(4);
Adafruit_DCMotor *feedDCMotor = AFMS.getMotor(3);
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRBW + NEO_KHZ800);

void handlePreviousState ()
{
  switch (state)
  {
    case GOT_L:
//      processLED (currentValue);
      break;
    case GOT_S:
      processStepper (currentValue);
      break;
    case GOT_X:
      processStopAll (currentValue);
      break;
  }  // end of switch

  currentValue = 0;
}  // end of handlePreviousState

void processIncomingByte (const byte c)
{
  if (isdigit (c))
  {
    currentValue *= 10;
    currentValue += c - '0';
  }  // end of digit
  else
  {

    // The end of the number signals a state change
    handlePreviousState ();

    // set the new state, if we recognize it
    switch (c)
    {
      case 'L':
        state = GOT_L;
        break;
      case 'S':
        state = GOT_S;
        break;
      case 'X':
        state = GOT_X;
        break;
      default:
        state = NONE;
        break;
    }  // end of switch on incoming byte
  } // end of not digit

} // end of processIncomingByte

//void processLED (const unsigned int value)
//{
//  if (value == 1) {
//    for (uint16_t i = 0; i < strip.numPixels(); i++) {
//      strip.setPixelColor(i, strip.Color(0, 0, 0, 255));
//    }
//    strip.show();
//  }
//  else if (value == 0) {
//    for (uint16_t i = 0; i < strip.numPixels(); i++) {
//      strip.setPixelColor(i, strip.Color(0, 0, 0, 0));
//    }
//    strip.show();
//  }
//} // end of processLED

void processStepper (const unsigned int value)
{
  myStepper->step(value, BACKWARD, DOUBLE);
  Serial.println("M");
} // end of processStepper

void processStopAll (const unsigned int value)
{
  takeupDCMotor->run(RELEASE);
  feedDCMotor->run(RELEASE);
  myStepper->release();
} // end of processStartStop


void setup() {
  Serial.begin(115200);

  state = NONE;

  AFMS.begin();  // create with the default frequency 1.6KHz
  myStepper->setSpeed(100);  // 10 rpm
  takeupDCMotor->setSpeed(25);
  takeupDCMotor->run(RELEASE);
  feedDCMotor->setSpeed(25);
  feedDCMotor->run(RELEASE);
  strip.setBrightness(BRIGHTNESS);
  strip.begin();
//  processLED(0);
}

void loop() {

  int potValuetakeup = analogRead(A1);

  if (potValuetakeup < takeupPotTrigger)
  {
    if (!takeupDCMotorRunning) {
//      Serial.println("Motor Run");
      takeupDCMotor->run(FORWARD);
      takeupDCMotorRunning = true;
    }
  }

  if (potValuetakeup > takeupPotKiller) {
    if (takeupDCMotorRunning) {
//      Serial.println("Motor Stop");
      takeupDCMotor->run(RELEASE);
      takeupDCMotorRunning = false;
    }
  }


  int potValuefeed = analogRead(A2);

  if (potValuefeed > feedPotTrigger)
  {
    if (!feedDCMotorRunning) {
//      Serial.println("Motor Run");
      feedDCMotor->run(FORWARD);
      feedDCMotorRunning = true;
    }
  }

  if (potValuefeed < feedPotKiller) {
    if (feedDCMotorRunning) {
//      Serial.println("Motor Stop");
      feedDCMotor->run(RELEASE);
      feedDCMotorRunning = false;
    }
  }

  while (Serial.available ())
    processIncomingByte (Serial.read ());

}



