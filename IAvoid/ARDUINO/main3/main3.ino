// Q-Learning Obstacle Avoidance Robot in 5x5 Grid World - Arduino Uno
// Avec enregistrement de toutes les données d'apprentissage
// Terminologie : Cycle = ensemble complet du début au goal, Épisode = chaque action
#define ENA 2
#define IN1 22
#define IN2 23
#define IN3 24
#define IN4 25
#define ENB 3
#define TRIG_PIN 9
#define ECHO_PIN 10 
#define GRID_SIZE 5
#define NUM_ACTIONS 3
#define CELL_DIST 10
#define MOVE_TIME 300

#define TURN_TIME 700
#define ACTION_WAIT 1000
#define RESET_DELAY 10000
#define MAX_STEPS 50

// Q-LEARNING HYPERPARAMETERS - OPTIMISÉS
#define LEARNING_RATE 0.5      // Apprentissage rapide
#define DISCOUNT 0.9           // Focus objectif proche
#define EPSILON 0.3            
#define EPSILON_MIN 0.05       // 5% exploration minimale
#define EPSILON_DECAY 0.95     // Décroissance rapide
#define NUM_CYCLES 50         

// Tables Q-learning
int8_t Q[GRID_SIZE][GRID_SIZE][4][NUM_ACTIONS] = {0};

// Variables d'état
int pos_x = 0, pos_y = 0, facing = 1;
int goal_x = 4, goal_y = 4;
bool known_obstacles[GRID_SIZE][GRID_SIZE] = {false};
float epsilon = EPSILON;

// TABLEAUX D'ENREGISTREMENT DES DONNÉES - OPTIMISÉS
int8_t cycle_steps[NUM_CYCLES];        // Nombre d'épisodes (actions) par cycle
int cycle_rewards[NUM_CYCLES];         // Récompense totale par cycle (int au lieu de float)
byte cycle_success[NUM_CYCLES];        // 0=échec, 1=succès (byte au lieu de bool)

// Statistiques en temps réel (pas de stockage complet)
int current_cycle = 0;
int current_episodes = 0;
int current_reward = 0;
unsigned long cycle_start_time = 0;

// Constantes
const int deltas[4][2] = {{-1, 0}, {0, 1}, {1, 0}, {0, -1}};
const char* dir_names[4] = {"North", "East", "South", "West"};
const char* action_names[3] = {"FORWARD", "TURN_LEFT", "TURN_RIGHT"};

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  Serial.begin(9600);
  randomSeed(analogRead(0));
  
  // Initialisation des tableaux
  for (int i = 0; i < NUM_CYCLES; i++) {
    cycle_steps[i] = 0;
    cycle_rewards[i] = 0;
    cycle_success[i] = 0;
  }
  
  Serial.println(F("=== Q-Learning Robot - Mémoire Optimisée ==="));
  Serial.println(F("Start: (0,0) facing East | Goal: (4,4)"));
  Serial.println(F("Cycles: 50 | Terminologie: Cycle = parcours, Épisode = action"));
  Serial.println(F("Début de l'apprentissage...\n"));
  initializeQWithPreferred();
  blinkDuringReset();
}

void blinkOnAction() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);
  delay(100);
}

void blinkDuringReset() {
  unsigned long startTime = millis();
  bool ledState = false;
  
  Serial.println(F("=== FIN DE CYCLE === Repos 10s ==="));
  
  while (millis() - startTime < RESET_DELAY) {
    if ((millis() - startTime) % 1000 < 500) {
      if (!ledState) {
        digitalWrite(LED_BUILTIN, HIGH);
        ledState = true;
      }
    } else {
      if (ledState) {
        digitalWrite(LED_BUILTIN, LOW);
        ledState = false;
      }
    }
    delay(10);
  }
  digitalWrite(LED_BUILTIN, LOW);
}

void initializeQWithPreferred() {
  int sim_x = 0, sim_y = 0, sim_f = 1;
  float bonus = 50.0;
  for (int i = 0; i < 4; i++) {
    Q[sim_x][sim_y][sim_f][0] += bonus;
    sim_y += deltas[sim_f][1];
  }
  Q[sim_x][sim_y][sim_f][2] += bonus;
  sim_f = (sim_f + 1) % 4;
  for (int i = 0; i < 4; i++) {
    Q[sim_x][sim_y][sim_f][0] += bonus;
    sim_x += deltas[sim_f][0];
  }
}

int getDistance() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  return duration * 0.034 / 2;
}

bool revealNeighborhood() {
  int dx = deltas[facing][0];
  int dy = deltas[facing][1];
  int nx = pos_x + dx;
  int ny = pos_y + dy;
  if (nx >= 0 && nx < GRID_SIZE && ny >= 0 && ny < GRID_SIZE) {
    int dist = getDistance();
    if (dist < CELL_DIST && !known_obstacles[nx][ny]) {
      known_obstacles[nx][ny] = true;
      Serial.print(F(">>> OBSTACLE en ("));
      Serial.print(nx); Serial.print(","); Serial.print(ny);
      Serial.println(F(")"));
      
      // VÉRIFIER SI OBSTACLE AU GOAL
      if (nx == goal_x && ny == goal_y) {
        Serial.println(F("!!!!! OBSTACLE AU GOAL (4,4) - CYCLE INVALIDE !!!!!"));
        return true;  // Signaler qu'il faut redémarrer le cycle
      }
    }
  }
  return false;  // Pas d'obstacle au goal
}

void reset() {
  pos_x = 0;
  pos_y = 0;
  facing = 1;
  memset(known_obstacles, 0, sizeof(known_obstacles));
  
  // Vérifier si obstacle au goal dès le début
  if (revealNeighborhood()) {
    // Obstacle au goal détecté - attendre repositionnement
    Serial.println(F(">>> Attente repositionnement obstacle du goal - nouveau cycle..."));
    blinkDuringReset();
    reset();  // Réessayer le cycle
  }
}

int chooseAction() {
  if (random(1000) / 1000.0 < epsilon) {
    return random(NUM_ACTIONS);
  } else {
    int best = 0;
    for (int a = 1; a < NUM_ACTIONS; a++) {
      if (Q[pos_x][pos_y][facing][a] > Q[pos_x][pos_y][facing][best]) best = a;
    }
    return best;
  }
}

float executeAction(int action, int step) {
  float reward = 0;
  
  // Affichage simplifié
  Serial.print(F("E"));
  Serial.print(step);
  Serial.print(F(": "));
  Serial.print(action_names[action]);
  Serial.print(F(" ("));
  Serial.print(pos_x); Serial.print(","); Serial.print(pos_y);
  Serial.print(F(")"));
  
  blinkOnAction();
  
  if (action == 1) { // turn left
    turnLeft(TURN_TIME-20);
    facing = (facing - 1 + 4) % 4;
    reward = -1;
    Serial.println(F(" -1"));
  }
  else if (action == 2) { // turn right
    turnRight(TURN_TIME);
    facing = (facing + 1) % 4;
    reward = -1;
    Serial.println(F(" -1"));
  }
  else { // forward
    int dx = deltas[facing][0];
    int dy = deltas[facing][1];
    int nx = pos_x + dx;
    int ny = pos_y + dy;
    if (nx < 0 || nx >= GRID_SIZE || ny < 0 || ny >= GRID_SIZE) {
      Serial.println(F(" MUR -5"));
      reward = -5;
    }
    else if (known_obstacles[nx][ny]) {
      Serial.print(F(" OBS("));
      Serial.print(nx); Serial.print(","); Serial.print(ny);
      Serial.println(F(") -10"));
      reward = -10;
      
      if (nx == goal_x && ny == goal_y) {
        reward = -999;
      }
    }
    else {
      int dist = getDistance();
      if (dist < CELL_DIST) {
        known_obstacles[nx][ny] = true;
        Serial.print(F(" NEW_OBS("));
        Serial.print(nx); Serial.print(","); Serial.print(ny);
        Serial.println(F(") -10"));
        reward = -10;
        
        if (nx == goal_x && ny == goal_y) {
          Serial.println(F("!!! GOAL BLOQUÉ !!!"));
          reward = -999;
        }
      }
      else {
        moveForward(MOVE_TIME);
        pos_x = nx;
        pos_y = ny;
        reward = -1;
        Serial.println(F(" -1"));
      }
    }
  }
  
  if (pos_x == goal_x && pos_y == goal_y) {
    Serial.println(F(">>> GOAL +100 <<<"));
    reward = 100;
  }
  
  revealNeighborhood();
  //delay(ACTION_WAIT);
  return reward;
}

void moveForward(int ms) {
  analogWrite(ENA, 200); analogWrite(ENB, 200);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  delay(ms);
  stopMotors();
}

void turnLeft(int ms) {
  analogWrite(ENA, 180); analogWrite(ENB, 180);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  delay(ms);
  stopMotors();
}

void turnRight(int ms) {
  analogWrite(ENA, 180); analogWrite(ENB, 180);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  delay(ms);
  stopMotors();
}

void stopMotors() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

// FONCTION POUR AFFICHER LES STATISTIQUES - SIMPLIFIÉ
void printStatistics() {
  Serial.println(F("\n===== STATISTIQUES ====="));
  Serial.println(F("Cycle,Episodes,Reward,Success"));
  
  int total_episodes = 0;
  long total_rewards = 0;
  int success_count = 0;
  
  for (int i = 0; i < NUM_CYCLES; i++) {
    Serial.print(i + 1); Serial.print(",");
    Serial.print(cycle_steps[i]); Serial.print(",");
    Serial.print(cycle_rewards[i]); Serial.print(",");
    Serial.println(cycle_success[i]);
    
    total_episodes += cycle_steps[i];
    total_rewards += cycle_rewards[i];
    if (cycle_success[i]) success_count++;
  }
  
  Serial.println(F("\n--- RÉSUMÉ ---"));
  Serial.print(F("Moy épisodes: "));
  Serial.println((float)total_episodes / NUM_CYCLES);
  Serial.print(F("Moy reward: "));
  Serial.println((float)total_rewards / NUM_CYCLES);
  Serial.print(F("Succès: "));
  Serial.print((float)success_count * 100 / NUM_CYCLES);
  Serial.println(F("%"));
}

void loop() {
  /*
  // Chemin Préféré
  executeAction(0, 1);
  executeAction(0, 2);
  executeAction(0, 3);
  executeAction(0, 4);
  executeAction(2, 5);
  executeAction(0, 6);
  executeAction(0, 7);
  executeAction(0, 8);
  executeAction(0, 9);
  blinkDuringReset();
  reset();*/
  static int cycle = 0;
  
  if (cycle >= NUM_CYCLES) {
    // AFFICHER LES STATISTIQUES
    printStatistics();
    
    Serial.println(F("\n=== MODE EXPLOITATION ==="));
    epsilon = 0;
    reset();
    
    while (true) {
      int action = chooseAction();
      executeAction(action, 0);
      if (pos_x == goal_x && pos_y == goal_y) {
        blinkDuringReset();
        reset();
      }
    }
  }
  
  // DÉBUT DU CYCLE
  reset();
  
  bool done = false;
  bool cycle_invalid = false;
  int episodes = 0;
  int total_reward = 0;
  
  Serial.print(F("\n--- Cycle "));
  Serial.print(cycle + 1);
  Serial.print(F(" (eps="));
  Serial.print(epsilon, 2);
  Serial.println(F(") ---"));
  
  while (!done && episodes < MAX_STEPS) {
    int action = chooseAction();
    int old_x = pos_x, old_y = pos_y, old_f = facing;
    
    float reward = executeAction(action, episodes);
    total_reward += (int)reward;
    
    // VÉRIFIER SI OBSTACLE AU GOAL
    if (reward == -999) {
      Serial.println(F(">>> REDÉMARRAGE CYCLE <<<"));
      cycle_invalid = true;
      blinkDuringReset();
      break;
    }
    
    if (pos_x == goal_x && pos_y == goal_y) done = true;
    
    // Mise à jour Q
    int8_t max_next = Q[pos_x][pos_y][facing][0];
    for (int a = 1; a < NUM_ACTIONS; a++) {
      if (Q[pos_x][pos_y][facing][a] > max_next) max_next = Q[pos_x][pos_y][facing][a];
    }
    
    Q[old_x][old_y][old_f][action] = (int8_t)constrain(
      Q[old_x][old_y][old_f][action] + (int8_t)round(LEARNING_RATE * 4 * (reward + DISCOUNT * max_next - Q[old_x][old_y][old_f][action])),
      -128, 127
    );
    
    episodes++;
  }
  
  // ENREGISTRER LES DONNÉES
  if (!cycle_invalid) {
    cycle_steps[cycle] = episodes;
    cycle_rewards[cycle] = total_reward;
    cycle_success[cycle] = done ? 1 : 0;
    
    Serial.print(F("Fin: "));
    Serial.print(episodes);
    Serial.print(F(" ep, R="));
    Serial.print(total_reward);
    if (done) Serial.println(F(" GOAL!"));
    else Serial.println();
    
    epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY);
    blinkDuringReset();
    cycle++;
  }
}
