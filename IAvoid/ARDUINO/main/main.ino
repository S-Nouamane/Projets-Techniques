// Q-Learning Obstacle Avoidance Robot - Arduino Uno
// 1 Ultrasonic HC-SR04 (front)
// Motor pins (L298N example)
#define ENA 5    // PWM right motor
#define IN1 6
#define IN2 7
#define IN3 8
#define IN4 9
#define ENB 10   // PWM left motor

#define TRIG_PIN 11
#define ECHO_PIN 12

#define NUM_STATES 10     // 0: very close ... 9: far
#define NUM_ACTIONS 3     // 0: forward, 1: turn left, 2: turn right
#define SAFE_DIST 30      // cm
#define LEARNING_RATE 0.9
#define DISCOUNT 0.95
#define EPSILON 0.55       // exploration rate (diminue avec le temps si voulu)

float Q[NUM_STATES][NUM_ACTIONS] = {0};  // Q-table
int current_state;
float epsilon = EPSILON;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  Serial.begin(9600);
  randomSeed(analogRead(0));
}

int getDistance() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  return duration * 0.034 / 2;
}

int getState(int dist) {
  if (dist < 5) return 0;                 // collision
  if (dist < 10) return 1;
  // ... découpe en 10 bandes
  return min(9, dist / 20);               // exemple simplifié
}

void executeAction(int action) {
  if (action == 0) { // forward
    analogWrite(ENA, 200); analogWrite(ENB, 200);
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    delay(500);  // avance 0.5s
  } else if (action == 1) { // turn left
    analogWrite(ENA, 180); analogWrite(ENB, 180);
    digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    delay(400);
  } else { // turn right
    analogWrite(ENA, 180); analogWrite(ENB, 180);
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    delay(400);
  }
  stopMotors();
}

void stopMotors() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

float getReward(int state, int action) {
  if (state == 0) return -100;            // collision → gros malus
  if (action == 0 && state > 5) return 10; // avance quand clair → bonus
  return -1;                              // petit malus par défaut
}

void loop() {
  int dist = getDistance();
  current_state = getState(dist);

  // Choisir action (epsilon-greedy)
  int action;
  if (random(1000) / 1000.0 < epsilon) {
    action = random(NUM_ACTIONS);         // exploration
  } else {
    action = 0;
    for (int a = 1; a < NUM_ACTIONS; a++) {
      if (Q[current_state][a] > Q[current_state][action]) action = a;
    }
  }

  int old_state = current_state;
  executeAction(action);

  dist = getDistance();                     // nouveau état
  int new_state = getState(dist);

  float reward = getReward(new_state, action);

  // Update Q-table
  float max_next = Q[new_state][0];
  for (int a = 1; a < NUM_ACTIONS; a++) {
    if (Q[new_state][a] > max_next) max_next = Q[new_state][a];
  }
  Q[old_state][action] += LEARNING_RATE * (reward + DISCOUNT * max_next - Q[old_state][action]);

  Serial.print("State: "); Serial.print(old_state);
  Serial.print(" Action: "); Serial.print(action);
  Serial.print(" Reward: "); Serial.println(reward);

  // Optionnel : diminuer epsilon avec le temps
  // if (epsilon > 0.01) epsilon *= 0.999;
}
