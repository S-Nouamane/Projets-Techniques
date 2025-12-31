// Déclaration des broches du codeur incrémental
const int pinA = 2; // Broche A du codeur connectée à la broche 2 d'Arduino (interrupt 0)
const int pinB = 3; // Broche B du codeur connectée à la broche 3 d'Arduino
const int IN2 = 10;
const int IN1 = 11;
const int ENA = 9;

// Variables pour le comptage des impulsions du codeur
volatile int pulseCount = 0; // Compteur d'impulsions
int previousPulseCount = 0; // Nombre d'impulsions précédent pour le calcul de la vitesse
unsigned long previousMillis = 0; // Temps précédent pour le calcul du délai
unsigned long interval = 50000; // Intervalle de temps pour le calcul de la vitesse (en Microsecondes)
int pulseParRevolution = 48;

// Variable asservissement
const float kp = 4310;
const float ki = 4310/1.32;
const int max_pwm = 255;
const int teta_c = 180;
float teta = 0;
float erreur = 0;
float somme_erreur = 0;
float speed = 0;
float var = 0;
const float r = 0.057438;

void setup() {
  // Initialisation des broches du codeur
  pinMode(pinA, INPUT);
  pinMode(pinB, INPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);

  // Activation de l'interruption pour la broche A (interrupt 0)
  attachInterrupt(digitalPinToInterrupt(pinA), countPulse, RISING);
  attachInterrupt(digitalPinToInterrupt(pinB), countPulse, RISING);
  attachInterrupt(digitalPinToInterrupt(pinA), countPulse, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinB), countPulse, FALLING);

  // Démarrage de la communication série
  Serial.begin(9600);
  Serial.println("t;teta(t);wr(t);erreur;pwm");
  Serial.print("0;0.00;0.00;");
  Serial.print(teta_c-teta);
  Serial.println(";0.00");
}

void loop() {
  unsigned long currentMillis = micros();

  // Calcul du temps écoulé depuis le dernier calcul de vitesse
  if (currentMillis - previousMillis >= interval) {
    // bloc d'asservissement
    teta += speed * interval / 1000000.00;
    erreur = teta_c - teta;
    somme_erreur += erreur * interval / 1000000.00;
    var = kp * erreur + ki * somme_erreur;

    // Enregistrement du nombre d'impulsions pendant l'intervalle
    float A = pulseCount - previousPulseCount;
    // Calcul de la vitesse en impulsions par seconde
    speed = 360*(float)A / (float)interval / pulseParRevolution * 1000000.0; // °/s
    speed *= r; // sortie reducteur

    if (var > 0) {
      digitalWrite(IN1, 1);
      digitalWrite(IN2, 0);
    } else {
      digitalWrite(IN1, 0);
      digitalWrite(IN2, 1);
      speed *= -1;
      var *= -1;
    }

    if (var > max_pwm){
      var = max_pwm;
    }
    analogWrite(ENA, var);

    // Affichage
    Serial.print(currentMillis);
    Serial.print(";");
    Serial.print(teta);
    Serial.print(";");
    Serial.print(speed);
    Serial.print(";");
    Serial.print(teta_c-teta);
    Serial.print(";");
    Serial.println(var);

    // Mise à jour des variables pour le prochain calcul de vitesse
    previousMillis = currentMillis;
    previousPulseCount = pulseCount;
  }
}

void countPulse() {
  // Augmentation du compteur d'impulsions à chaque interruption
  pulseCount++;
}
