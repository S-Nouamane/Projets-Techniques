import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
from datetime import datetime

# Configuration
RUN_FILES = [f'comparaison paramètres/comparisons learning_rate/2101/episode_data_learningrate{i}.xlsx' for i in range(1, 6)]  # Fichiers de 01 à 05
OUTPUT_DIR = 'comparaison paramètres/comparisons learning_rate'
parametres_change = [0.3, 0.4, 0.5, 0.7, 0.9]
GRID_SIZE = 15
NUM_EPISODES = 5000
WINDOW_SIZE = 50  # Taille de la fenêtre pour la moyenne mobile (épisodes)
CYCLE_WINDOW_SIZE = 5  # Taille de la fenêtre pour la moyenne mobile (cycles)
os.makedirs(OUTPUT_DIR, exist_ok=True)
DATE_STR = str("20251205_2101") #datetime.now().strftime('%Y%m%d_%H%M')  # Ex. : 20251010_0943

# Charger et fusionner les données
dataframes = []
for i, file in enumerate(RUN_FILES, 1):
    if os.path.exists(file):
        df = pd.read_excel(file, sheet_name='EpisodeData')
        df['run'] = f'Run {i:02d} {parametres_change[i-1]}'  # Ajouter une colonne pour identifier le run
        dataframes.append(df)
    else:
        print(f"Warning: {file} not found, skipping.")
combined_df = pd.concat(dataframes, ignore_index=True)

# Ajouter les colonnes lissées basées sur les données non lissées
combined_df['reward_smoothed'] = combined_df['total_reward'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
combined_df['steps_smoothed'] = combined_df['steps'].rolling(window=WINDOW_SIZE, min_periods=1).mean()

# Calculer le taux de succès lissé par cycle (basé sur les données non lissées)
success_rate = combined_df.groupby(['cycle', 'run'])['reached_goal'].mean().reset_index()
success_rate_pivot = success_rate.pivot(index='cycle', columns='run', values='reached_goal')
original_runs = success_rate_pivot.columns.tolist()
for run in original_runs:
    success_rate_pivot[f'{run}_smoothed'] = success_rate_pivot[run].rolling(window=CYCLE_WINDOW_SIZE, min_periods=1).mean()

# Fonction pour sauvegarder un graphique
def save_plot(fig, name):
    filename = f"{name}_grid{GRID_SIZE}_ep{NUM_EPISODES}_smoothed_{DATE_STR}_{len(RUN_FILES)}runs.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath)
    print(f"Graphique sauvegardé : {filepath}")

# 1. Heatmap des positions visitées (comparaison côte à côte)
n_runs = len(RUN_FILES)
fig, axes = plt.subplots(1, n_runs, figsize=(5 * n_runs, 5), sharey=True)
for idx, (df_run, ax) in enumerate(zip(dataframes, axes)):
    positions = []
    for path_str in df_run['path']:
        path_list = path_str.split(';')
        for pos in path_list:
            if pos.strip():
                x, y, _ = pos.strip('()').split(',')
                positions.append((int(x), int(y)))
    pos_count = Counter(positions)
    heatmap_data = pd.DataFrame(0, index=range(GRID_SIZE), columns=range(GRID_SIZE))
    for (x, y), count in pos_count.items():
        heatmap_data.at[x, y] = count
    sns.heatmap(heatmap_data, annot=False, cmap='YlGnBu', ax=ax, cbar=idx == n_runs-1)
    ax.set_title(f'Run {idx+1:02d} {parametres_change[idx]}')
plt.suptitle('Heatmap des positions visitées par run')
save_plot(plt, 'positions_heatmap_comparison')
plt.tight_layout()
plt.show()

# 2. Comparaison des récompenses totales par épisode (moyenne lissée)
plt.figure(figsize=(12, 6))
sns.lineplot(x='episode', y='reward_smoothed', hue='run', data=combined_df)
plt.title('Comparaison des récompenses totales lissées par épisode')
plt.xlabel('Épisode')
plt.ylabel('Récompense totale (moyenne mobile, fenêtre 50)')
plt.legend(title='Run')
save_plot(plt, 'reward_comparison_smoothed')
plt.show()

# 3. Taux de succès moyen par cycle (moyenne lissée)
plt.figure(figsize=(12, 6))
for run in original_runs:
    plt.plot(success_rate_pivot.index, success_rate_pivot[f'{run}_smoothed'], label=run, marker='o')
plt.title('Taux de succès moyen lissé par cycle')
plt.xlabel('Cycle')
plt.ylabel('Taux de succès (moyenne mobile, fenêtre 5)')
plt.legend(title='Run')
save_plot(plt, 'success_rate_comparison_smoothed')
plt.show()

# 4. Récompenses vs nombre de pas (moyenne lissée)
agg_df = combined_df.groupby(['episode', 'run']).agg({'reward_smoothed': 'mean', 'steps_smoothed': 'mean'}).reset_index()
plt.figure(figsize=(12, 6))
sns.scatterplot(x='steps_smoothed', y='reward_smoothed', hue='run', data=agg_df)
plt.title('Récompenses lissées vs nombre de pas lissés par run')
plt.xlabel('Nombre de pas (moyenne mobile, fenêtre 50)')
plt.ylabel('Récompense totale (moyenne mobile, fenêtre 50)')
plt.legend(title='Run')
save_plot(plt, 'reward_vs_steps_smoothed_comparison')
plt.show()