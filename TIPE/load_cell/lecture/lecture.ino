#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 Demo");

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  //103 pour flexion sur léextrimité
  //xx pour flexion au milieu
  scale.set_scale(103); // cette valeur est obtenue en calibrant l'échelle avec des poids connus 103
  scale.tare(); // réinitialise l'échelle à 0

  Serial.println("Readings:");
}

void loop() {
  float weight = scale.get_units(10);
  if (weight < 0) {
    weight = 0;
  } 
  Serial.print("Masse: ");
  Serial.print(weight, 1);
  Serial.println(" g");

  delay(1000);
}
