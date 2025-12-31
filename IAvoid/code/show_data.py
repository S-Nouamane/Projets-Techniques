import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast  # Pour parser obstacle_config si besoin
from collections import Counter
import os

# Hyperparamètres pour nommer les fichiers (adaptez selon votre run)
GRID_SIZE = 15
NUM_EPISODES = 5000
OUTPUT_DIR = 'graphs_presentation'  # Dossier de sortie
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Charger les données
df = pd.read_excel('episode_data_learningrate1.xlsx', sheet_name='EpisodeData')

# Fonction pour sauvegarder un graphique avec nom paramétré
def save_plot(fig, name):
    filename = f"{name}_grid{GRID_SIZE}_ep{NUM_EPISODES}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath)
    print(f"Graphique sauvegardé : {filepath}")

# 1. Courbe d'évolution des récompenses
plt.figure(figsize=(10, 6))
sns.lineplot(x='episode', y='total_reward', data=df, label='Récompense totale')
df['reward_smoothed'] = df['total_reward'].rolling(window=50).mean()  # Moyenne mobile
sns.lineplot(x='episode', y='reward_smoothed', data=df, color='red', label='Moyenne mobile')
plt.title('Évolution des récompenses totales par épisode')
plt.xlabel('Épisode')
plt.ylabel('Récompense totale')
save_plot(plt, 'reward_over_episodes')
plt.show()

# 2. Courbe d'évolution des steps
plt.figure(figsize=(10, 6))
sns.lineplot(x='episode', y='steps', data=df)
plt.title('Évolution du nombre de pas par épisode')
plt.xlabel('Épisode')
plt.ylabel('Nombre de pas')
save_plot(plt, 'steps_over_episodes')
plt.show()

# 3. Taux de succès par cycle
success_rate = df.groupby('cycle')['reached_goal'].mean().reset_index()
plt.figure(figsize=(10, 6))
sns.barplot(x='cycle', y='reached_goal', data=success_rate)
plt.title('Taux de succès moyen par cycle')
plt.xlabel('Cycle')
plt.ylabel('Taux de succès (0-1)')
save_plot(plt, 'success_rate_per_cycle')
plt.show()

# 4. Histogramme des récompenses
plt.figure(figsize=(10, 6))
sns.histplot(df['total_reward'], bins=20, kde=True)
plt.title('Distribution des récompenses totales')
plt.xlabel('Récompense totale')
plt.ylabel('Fréquence')
save_plot(plt, 'reward_histogram')
plt.show()

# 5. Nuage de points : Récompenses vs. Steps
plt.figure(figsize=(10, 6))
sns.scatterplot(x='steps', y='total_reward', hue='cycle', data=df)
plt.title('Récompenses vs. Nombre de pas (coloré par cycle)')
plt.xlabel('Nombre de pas')
plt.ylabel('Récompense totale')
save_plot(plt, 'reward_vs_steps_scatter')
plt.show()

# 6. Heatmap de positions visitées (exemple pour tous les épisodes)
positions = []
for path_str in df['path']:
    path_list = path_str.split(';')
    for pos in path_list:
        if pos.strip():  # Ignorer vides
            x, y, _ = pos.strip('()').split(',')
            positions.append((int(x), int(y)))
pos_count = Counter(positions)
heatmap_data = pd.DataFrame(0, index=range(GRID_SIZE), columns=range(GRID_SIZE))
for (x, y), count in pos_count.items():
    heatmap_data.at[x, y] = count
plt.figure(figsize=(10, 10))
sns.heatmap(heatmap_data, annot=False, cmap='YlGnBu')
plt.title('Heatmap des positions visitées (fréquence)')
plt.xlabel('Y')
plt.ylabel('X')
save_plot(plt, 'positions_heatmap')
plt.show()

# 7. Boîte à moustaches des récompenses par cycle
plt.figure(figsize=(10, 6))
sns.boxplot(x='cycle', y='total_reward', data=df)
plt.title('Distribution des récompenses par cycle')
plt.xlabel('Cycle')
plt.ylabel('Récompense totale')
save_plot(plt, 'reward_boxplot_per_cycle')
plt.show()

# 8. Courbe d'apprentissage lissée (similaire au 1, mais standalone si besoin)
# (Déjà inclus dans le graphique 1)