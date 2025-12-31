#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 calibration");

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale();
  scale.tare(); // réinitialise l'échelle à 0

  Serial.println("Placez un poids connu sur la balance, puis ouvrez le moniteur série...");
}

void loop() {
  if(Serial.available())
  {
    char temp = Serial.read();
    if(temp == '+' || temp == 'a')
    {
      scale.set_scale(scale.get_scale() + 1);
    }
    else if(temp == '-' || temp == 'z')
    {
      scale.set_scale(scale.get_scale() - 1);
    }
  }

  Serial.print("Lecture : ");
  Serial.print(scale.get_units(), 1);
  Serial.print(" g");
  Serial.print(" facteur d'échelle : ");
  Serial.println(scale.get_scale());

  delay(500);
}
