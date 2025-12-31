import pygame
import sys
import numpy as np
import random
import pandas as pd
import time
from collections import deque
import argparse
import uuid

# -------------------------
# Hyperparameters
# -------------------------
# 
learning_rate = 0.3     
discount_factor = 0.9      
epsilon = 0.7              
epsilon_min = 0.01          
epsilon_decay = 0.997       
num_episodes = 5000         
grid_size = 15              
obstacle_change_interval = 200  
max_steps_per_episode = 250    
cell_size = 40
screen_size = grid_size * cell_size
tick_time = 240              
episodes_output = "episode_data.xlsx"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
PINK = (255, 170, 170)
GREEN = (0, 200, 0)
BLUE = (30, 144, 255)
GREY = (200, 200, 200)

# Directions: 0-North (up), 1-East (right), 2-South (down), 3-West (left)
deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)]
dir_names = ['North', 'East', 'South', 'West']

# Actions: 0-forward, 1-turn_left, 2-turn_right
action_names = ['forward', 'turn_left', 'turn_right']
act_chars = ['F', 'L', 'R']
action_to_idx = {name: idx for idx, name in enumerate(action_names)}

# -------------------------
# Environment class
# -------------------------
class Environment:
    def __init__(self):
        self.start_pos = (0, 0)
        self.start_facing = 1  # East
        self.goal = (grid_size - 1, grid_size - 1)
        self.true_obstacles = set()
        self.known_obstacles = set()
        self.position = self.start_pos
        self.facing = self.start_facing

    def reset(self, keep_known=False):
        self.position = self.start_pos
        self.facing = self.start_facing
        if not keep_known:
            self.known_obstacles = set()
        self.reveal_neighborhood()
        return (self.position[0], self.position[1], self.facing)

    def add_random_obstacles(self, num):
        self.true_obstacles = set()
        attempts = 0
        while len(self.true_obstacles) < num and attempts < num * 30:
            attempts += 1
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)
            coord = (x, y)
            if coord == self.start_pos or coord == self.goal:
                continue
            self.true_obstacles.add(coord)
        while not self.is_path_possible():
            if not self.true_obstacles:
                break
            self.true_obstacles.pop()

    def is_path_possible(self):
        visited = set()
        queue = deque([(self.start_pos, self.start_facing)])
        visited.add((self.start_pos[0], self.start_pos[1], self.start_facing))
        while queue:
            (x, y), f = queue.popleft()
            if (x, y) == self.goal:
                return True
            # Try forward
            dx, dy = deltas[f]
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in self.true_obstacles:
                if (nx, ny, f) not in visited:
                    visited.add((nx, ny, f))
                    queue.append(((nx, ny), f))
            # Try turn_left
            nf = (f - 1) % 4
            if (x, y, nf) not in visited:
                visited.add((x, y, nf))
                queue.append(((x, y), nf))
            # Try turn_right
            nf = (f + 1) % 4
            if (x, y, nf) not in visited:
                visited.add((x, y, nf))
                queue.append(((x, y), nf))
        return False

    def reveal_neighborhood(self):
        x, y = self.position
        dx, dy = deltas[self.facing]
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            coord = (nx, ny)
            if coord in self.true_obstacles:
                self.known_obstacles.add(coord)

    def step(self, action):
        done = False
        if action == 1:  # turn_left
            self.facing = (self.facing - 1) % 4
            reward = -1
            self.reveal_neighborhood()
            return (self.position[0], self.position[1], self.facing), reward, done
        elif action == 2:  # turn_right
            self.facing = (self.facing + 1) % 4
            reward = -1
            self.reveal_neighborhood()
            return (self.position[0], self.position[1], self.facing), reward, done

        # action == 0: forward
        dx, dy = deltas[self.facing]
        tx = max(0, min(self.position[0] + dx, grid_size - 1))
        ty = max(0, min(self.position[1] + dy, grid_size - 1))
        target = (tx, ty)

        if target == self.position:  # hit wall
            reward = -5
            self.reveal_neighborhood()
            return (self.position[0], self.position[1], self.facing), reward, done

        if target in self.true_obstacles:
            reward = -10
            self.reveal_neighborhood()
            return (self.position[0], self.position[1], self.facing), reward, done

        self.position = target
        self.reveal_neighborhood()
        if self.position == self.goal:
            reward = 100
            done = True
        else:
            reward = -1
        return (self.position[0], self.position[1], self.facing), reward, done

# -------------------------
# Utilities
# -------------------------
def get_obstacle_config_key(obstacles):
    return tuple(sorted(obstacles))

def draw_grid(screen, env, episode, cycle):
    screen.fill(WHITE)
    for x in range(0, screen_size, cell_size):
        pygame.draw.line(screen, GREY, (x, 0), (x, screen_size))
    for y in range(0, screen_size, cell_size):
        pygame.draw.line(screen, GREY, (0, y), (screen_size, y))

    for ox, oy in env.true_obstacles:
        pygame.draw.rect(screen, RED, (oy * cell_size, ox * cell_size, cell_size, cell_size))
    for ox, oy in env.known_obstacles:
        pygame.draw.rect(screen, PINK, (oy * cell_size + 6, ox * cell_size + 6, cell_size - 12, cell_size - 12))

    pygame.draw.rect(screen, BLUE, (env.start_pos[1] * cell_size, env.start_pos[0] * cell_size, cell_size, cell_size))
    pygame.draw.rect(screen, GREEN, (env.goal[1] * cell_size, env.goal[0] * cell_size, cell_size, cell_size))

    font = pygame.font.SysFont(None, 22)
    txt = font.render(f"Episode: {episode}/{num_episodes}  Cycle: {cycle}  Known: {len(env.known_obstacles)}", True, BLACK)
    screen.blit(txt, (8, 6))

def get_learned_path(env, Q, max_steps=max_steps_per_episode):
    sim_env = Environment()
    sim_env.start_pos = env.start_pos
    sim_env.start_facing = env.start_facing
    sim_env.goal = env.goal
    sim_env.true_obstacles = set(env.true_obstacles)
    state = sim_env.reset(keep_known=False)
    path = [state]
    done = False
    steps = 0
    while not done and steps < max_steps:
        x, y, f = state
        action = int(np.argmax(Q[x, y, f]))
        new_state, _, done = sim_env.step(action)
        path.append(new_state)
        state = new_state
        steps += 1
    return path

def animate_path(screen, path, env, episode, cycle, tick_time=60):
    index = 0
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    while index < len(path):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        draw_grid(screen, env, episode, cycle)
        x, y, f = path[index]
        cx = y * cell_size + cell_size // 2
        cy = x * cell_size + cell_size // 2
        radius = cell_size // 3
        pygame.draw.circle(screen, BLUE, (cx, cy), radius)
        drow, dcol = deltas[f]
        pygame.draw.line(screen, BLACK, (cx, cy), (cx + dcol * radius, cy + drow * radius), 3)
        txt = font.render(f"Step: {index}/{len(path)-1}", True, BLACK)
        screen.blit(txt, (10, 30))
        pygame.display.flip()
        clock.tick(tick_time)
        index += 1
    time.sleep(0.3)
    return True

def print_policy_to_console(Q, env):
    for f in range(4):
        print(f"\nPolicy facing {dir_names[f]} (S=start, G=goal, X=obst, F/L/R=actions):")
        for x in range(grid_size):
            row = []
            for y in range(grid_size):
                pos = (x, y)
                if pos == env.start_pos:
                    row.append('S ')
                elif pos == env.goal:
                    row.append('G ')
                elif pos in env.true_obstacles:
                    row.append('X ')
                else:
                    a = np.argmax(Q[x, y, f])
                    row.append(act_chars[a] + ' ')
            print(''.join(row))

def initialize_q_with_preferred_path(Q, preferred_path, env):
    sim_env = Environment()
    sim_env.start_pos = env.start_pos
    sim_env.start_facing = env.start_facing
    sim_env.goal = env.goal
    sim_env.true_obstacles = set()
    state = sim_env.reset(keep_known=False)
    q_bonus = 50.0
    for action_name in preferred_path:
        if action_name not in action_to_idx:
            print(f"Invalid action '{action_name}' in preferred path. Skipping.")
            continue
        action_idx = action_to_idx[action_name]
        x, y, f = state
        Q[x, y, f, action_idx] += q_bonus
        new_state, _, done = sim_env.step(action_idx)
        state = new_state
        if done:
            break

# -------------------------
# Excel/CSV append helper
# -------------------------
from openpyxl import load_workbook

def save_policies_append(policy_db, filename="policy_database.xlsx", use_csv=False):
    if use_csv:
        for idx, (config_key, q_table) in enumerate(policy_db.items()):
            rows = []
            for x in range(q_table.shape[0]):
                for y in range(q_table.shape[1]):
                    for f in range(4):
                        pos = (x, y)
                        if pos == (0, 0):
                            action = "Start"
                        elif pos == (q_table.shape[0] - 1, q_table.shape[1] - 1):
                            action = "Goal"
                        elif pos in config_key:
                            action = "Obstacle"
                        else:
                            action_idx = int(np.argmax(q_table[x, y, f]))
                            action = action_names[action_idx]
                        rows.append({
                            "x": x, "y": y, "facing": dir_names[f],
                            "action": action, "obstacle_config": str(config_key)
                        })
            df = pd.DataFrame(rows)
            csv_file = f"policy_config_{idx}_{len(config_key)}obs.csv"
            df.to_csv(csv_file, index=False)
            print(f"Policy saved to '{csv_file}'.")
    else:
        try:
            book = load_workbook(filename)
            existing_sheets = [ws.title for ws in book.worksheets]
            with pd.ExcelWriter(filename, engine="openpyxl", mode="a", if_sheet_exists="new") as writer:
                start_idx = len(existing_sheets)
                for idx, (config_key, q_table) in enumerate(policy_db.items(), start=start_idx):
                    rows = []
                    for x in range(q_table.shape[0]):
                        for y in range(q_table.shape[1]):
                            for f in range(4):
                                pos = (x, y)
                                if pos == (0, 0):
                                    action = "Start"
                                elif pos == (q_table.shape[0] - 1, q_table.shape[1] - 1):
                                    action = "Goal"
                                elif pos in config_key:
                                    action = "Obstacle"
                                else:
                                    action_idx = int(np.argmax(q_table[x, y, f]))
                                    action = action_names[action_idx]
                                rows.append({
                                    "x": x, "y": y, "facing": dir_names[f],
                                    "action": action, "obstacle_config": str(config_key)
                                })
                    df = pd.DataFrame(rows)
                    sheet_name = f"Config_{idx}_{len(config_key)}obs"
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        except FileNotFoundError:
            with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:
                for idx, (config_key, q_table) in enumerate(policy_db.items()):
                    rows = []
                    for x in range(q_table.shape[0]):
                        for y in range(q_table.shape[1]):
                            for f in range(4):
                                pos = (x, y)
                                if pos == (0, 0):
                                    action = "Start"
                                elif pos == (q_table.shape[0] - 1, q_table.shape[1] - 1):
                                    action = "Goal"
                                elif pos in config_key:
                                    action = "Obstacle"
                                else:
                                    action_idx = int(np.argmax(q_table[x, y, f]))
                                    action = action_names[action_idx]
                                rows.append({
                                    "x": x, "y": y, "facing": dir_names[f],
                                    "action": action, "obstacle_config": str(config_key)
                                })
                    df = pd.DataFrame(rows)
                    sheet_name = f"Config_{idx}_{len(config_key)}obs"
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        print(f"Policies appended to '{filename}'.")

# -------------------------
# Main training loop
# -------------------------
def main(preferred_path=None, no_render=False, use_csv=False):
    global epsilon
    pygame.init()
    screen = None if no_render else pygame.display.set_mode((screen_size, screen_size))
    if not no_render:
        pygame.display.set_caption('Q-Learning Partial Observability - Car-like Agent')

    env = Environment()
    Q = np.zeros((grid_size, grid_size, 4, 3))  # Updated for 3 actions
    policy_db_local = {}
    episode_data = []  # To store paths and rewards
    cycle = 0

    env.true_obstacles = set()
    env.reset(keep_known=False)
    if preferred_path:
        print(f"Applying preferred path for empty map: {preferred_path}")
        initialize_q_with_preferred_path(Q, preferred_path, env)

    for episode in range(num_episodes):
        if not no_render:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        if episode % obstacle_change_interval == 0:
            cycle += 1
            if episode == 0:
                env.true_obstacles = set()
                print(f"[Cycle {cycle}] Starting with empty obstacle map.")
            else:
                env.add_random_obstacles(max(4, int(grid_size * 0.8)))
                print(f"[Cycle {cycle}] New true obstacles set ({len(env.true_obstacles)} obstacles).")

        state = env.reset(keep_known=False)
        done = False
        steps = 0
        total_reward = 0
        path = [state]

        while not done and steps < max_steps_per_episode:
            steps += 1
            x, y, f = state
            if random.random() < epsilon:
                action = random.randint(0, 2)  # Updated for 3 actions
            else:
                action = int(np.argmax(Q[x, y, f]))

            new_state, reward, done = env.step(action)
            total_reward += reward
            path.append(new_state)
            nx, ny, nf = new_state
            best_next = int(np.argmax(Q[nx, ny, nf]))
            td_target = reward + discount_factor * Q[nx, ny, nf, best_next]
            td_error = td_target - Q[x, y, f, action]
            Q[x, y, f, action] += learning_rate * td_error
            state = new_state

        if not done:
            last_x, last_y, last_f = state
            Q[last_x, last_y, last_f, :] -= 0.02

        # Store episode data
        episode_data.append({
            'episode': episode + 1,
            'cycle': cycle,
            'path': path,
            'total_reward': total_reward,
            'steps': steps,
            'reached_goal': done,
            'obstacle_config': str(get_obstacle_config_key(env.true_obstacles))
        })

        print(f"[Cycle {cycle}] Episode {episode+1}/{num_episodes}: steps={steps}, reached={done}, eps={epsilon:.3f}, total_reward={total_reward:.2f}")

        if episode % obstacle_change_interval == obstacle_change_interval - 1 or episode == num_episodes - 1:
            cfg_key = get_obstacle_config_key(env.true_obstacles)
            policy_db_local[cfg_key] = Q.copy()
            print(f"[Cycle {cycle}] Snapshot saved for config (obs={len(cfg_key)}).")
            learned_path = get_learned_path(env, Q)
            print(f"[Cycle {cycle}] Learned path length: {len(learned_path)}")
            print_policy_to_console(Q, env)
            if not no_render:
                cont = animate_path(screen, learned_path, env, episode + 1, cycle, tick_time=int(tick_time / 2))
                if not cont:
                    break

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print('Training finished. Saving all snapshots and episode data.')
    # if policy_db_local:
    #     save_policies_append(policy_db_local, use_csv=use_csv)

    # Save episode data to CSV
    episode_df = pd.DataFrame([
        {
            'episode': data['episode'],
            'cycle': data['cycle'],
            'path': ';'.join([f"({x},{y},{dir_names[f]})" for x, y, f in data['path']]),
            'total_reward': data['total_reward'],
            'steps': data['steps'],
            'reached_goal': data['reached_goal'],
            'obstacle_config': data['obstacle_config']
        } for data in episode_data
    ])
    params_df = pd.DataFrame({
        'learning_rate': [learning_rate],
        'discount_factor': [discount_factor],
        'epsilon': [epsilon],
        'epsilon_min': [epsilon_min],
        'epsilon_decay': [epsilon_decay],
        'num_episodes': [num_episodes],
        'grid_size': [grid_size],
        'obstacle_change_interval': [obstacle_change_interval],
        'max_steps_per_episode': [max_steps_per_episode]
    })
    with pd.ExcelWriter(episodes_output, engine='openpyxl', mode='w') as writer:
        params_df.to_excel(writer, sheet_name='Hyperparameters', index=False)
        episode_df.to_excel(writer, sheet_name='EpisodeData', index=False)
    print(f"Episode data saved to {episodes_output}.")

    if not no_render:
        last_path = get_learned_path(env, Q)
        index = 0
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 22)
        running = True
        while running:
            for evt in pygame.event.get():
                if evt.type == pygame.QUIT:
                    running = False
            draw_grid(screen, env, num_episodes, cycle)
            if index < len(last_path):
                x, y, f = last_path[index]
                cx = y * cell_size + cell_size // 2
                cy = x * cell_size + cell_size // 2
                radius = cell_size // 3
                pygame.draw.circle(screen, BLUE, (cx, cy), radius)
                drow, dcol = deltas[f]
                pygame.draw.line(screen, BLACK, (cx, cy), (cx + dcol * radius, cy + drow * radius), 3)
                txt = font.render(f"Step: {index}/{len(last_path)-1}", True, BLACK)
                screen.blit(txt, (10, 30))
                index += 1
            else:
                index = 0
            pygame.display.flip()
            clock.tick(tick_time)

    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Q-Learning with Partial Observability')
    parser.add_argument('--no-render', action='store_true', help='Disable Pygame rendering')
    parser.add_argument('--use-csv', action='store_true', help='Save policies as CSV instead of Excel')
    args = parser.parse_args()

    preferred_path = ['forward']*(grid_size-1) + ['turn_right'] + ['forward']*(grid_size-1)
    main(preferred_path=preferred_path, no_render=args.no_render, use_csv=args.use_csv)