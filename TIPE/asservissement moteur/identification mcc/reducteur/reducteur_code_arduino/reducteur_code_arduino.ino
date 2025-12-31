// Déclaration des broches du codeur incrémental
const int pinA = 6; // Broche A du codeur connectée à la broche 2 d'Arduino (interrupt 0)
const int pinB = 7; // Broche B du codeur connectée à la broche 3 d'Arduino
const int pinAr = 2;
const int pinBr = 3;
const int IN2 = 10;
const int IN1 = 11;
const int ENA = 9;
const int pot = A0;

float wm = 0;
float wr = 0;

// Variables pour le comptage des impulsions du codeur
volatile int pulseCountM = 0; // Compteur d'impulsions
int previousPulseCountM = 0; // Nombre d'impulsions précédent pour le calcul de la vitesse
volatile int pulseCountR = 0;
int previousPulseCountR = 0;

unsigned long previousMillis = 0; // Temps précédent pour le calcul du délai
unsigned long interval = 1000000; // Intervalle de temps pour le calcul de la vitesse (en Microsecondes)
int pulseParRevolutionM = 24*4;
int pulseParRevolutionR = 30*4;
float pwm = 0;


void setup() {
  // Initialisation des broches du codeur
  pinMode(pinA, INPUT);
  pinMode(pinB, INPUT);
  pinMode(pinAr, INPUT);
  pinMode(pinBr, INPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(pot, INPUT); //entree

  // Activation de l'interruption pour la broche A (interrupt 0)
  attachInterrupt(digitalPinToInterrupt(pinA), countPulseM, RISING);
  attachInterrupt(digitalPinToInterrupt(pinB), countPulseM, RISING);
  attachInterrupt(digitalPinToInterrupt(pinA), countPulseM, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinB), countPulseM, FALLING);

  //pour capteur
  attachInterrupt(digitalPinToInterrupt(pinAr), countPulseR, RISING);
  attachInterrupt(digitalPinToInterrupt(pinBr), countPulseR, RISING);
  attachInterrupt(digitalPinToInterrupt(pinAr), countPulseR, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinBr), countPulseR, FALLING);

  // Démarrage de la communication série
  Serial.begin(9600);
  digitalWrite(IN1, 1);
  digitalWrite(IN2, 0);
  Serial.println("t;wm;wr");
  Serial.println("0;0;0");
}

void loop() {
  unsigned long currentMillis = micros();
  pwm = map(analogRead(pot), 0, 1023, 0, 255);
  analogWrite(ENA, pwm);

  // Calcul du temps écoulé depuis le dernier calcul de vitesse
  if (currentMillis - previousMillis >= interval) {
    // Enregistrement du nombre d'impulsions pendant l'intervalle
    int M = pulseCountM - previousPulseCountM;
    int R = pulseCountR - previousPulseCountR;
    // Calcul de la vitesse en impulsions par seconde
    wm = 2*PI*(float)M / (float)interval / pulseParRevolutionM * 1000000.0; // rad/s
    wr = 2*PI*(float)R / (float)interval / pulseParRevolutionR * 1000000.0;
    // Affichage de la vitesse
    Serial.print(currentMillis);
    Serial.print(";");
    Serial.print(wm);
    Serial.print(";");
    Serial.println(wr);


    // Mise à jour des variables pour le prochain calcul de vitesse
    previousMillis = currentMillis;
    previousPulseCountM = pulseCountM;
    previousPulseCountR = pulseCountR;
  }
}

void countPulseM() {
  // Augmentation du compteur d'impulsions à chaque interruption
  pulseCountM++;
}
void countPulseR() {
  // Augmentation du compteur d'impulsions à chaque interruption
  pulseCountR++;
}
