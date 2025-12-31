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
unsigned long interval = 100000; // Intervalle de temps pour le calcul de la vitesse (en Microsecondes)
int pulseParRevolution = 24*4;
float pwm = 0;
int temps_trainage = 5; //s
const int max_pwm = 255;


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
  digitalWrite(IN1, 1);
  digitalWrite(IN2, 0);
  Serial.println("t;w(t);pwm");
  Serial.println("0;0;0");
}

void loop() {
  unsigned long currentMillis = micros();
  pwm = max_pwm*currentMillis/(temps_trainage*1000000);
  analogWrite(ENA, pwm);

  // Calcul du temps écoulé depuis le dernier calcul de vitesse
  if (currentMillis - previousMillis >= interval) {
    // Enregistrement du nombre d'impulsions pendant l'intervalle
    pulseCount = pulseCount - previousPulseCount;
    // Calcul de la vitesse en impulsions par seconde
    float speed = 2*PI*(float)pulseCount / (float)interval / pulseParRevolution * 1000000.0; // rad/s

    // Affichage de la vitesse
    Serial.print(currentMillis);
    Serial.print(";");
    Serial.print(speed);
    Serial.print(";");
    Serial.println(pwm);


    // Mise à jour des variables pour le prochain calcul de vitesse
    previousMillis = currentMillis;
    previousPulseCount = pulseCount;
    if (pwm>=max_pwm){
      pwm = max_pwm;
    }
  }
}

void countPulse() {
  // Augmentation du compteur d'impulsions à chaque interruption
  pulseCount++;
}

