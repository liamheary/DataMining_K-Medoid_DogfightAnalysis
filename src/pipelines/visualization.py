
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

def infer_tactical_state(medoid_features):
    """Infers a tactical state based on key feature values."""
    # Example logic: High energy and low distance might be offensive
    if medoid_features['specific_energy_ratio'] > 0.6 and medoid_features['delta_distance'] < 0.4:
        return "High-Energy Offensive"
    elif medoid_features['specific_energy_ratio'] < 0.4:
        return "Low-Energy Defensive"
    else:
        return "Neutral/Transitional"

def create_visualization_dashboard(df, labels, medoids, features, output_path, tactical_labels):
    """Creates and saves a multi-panel visualization of the clustering results."""
    # 1. PCA for visualization
    pca = PCA(n_components=2)
    X = df[features].values
    principal_components = pca.fit_transform(X)
    pc_df = pd.DataFrame(data=principal_components, columns=['PC 1', 'PC 2'])
    pc_df['label'] = labels

    # Get medoid PCs
    medoid_pcs = pca.transform(medoids)

    # Infer tactical labels for the legend
    legend_mapping = {i: f'Cluster {i}: {label}' for i, label in enumerate(tactical_labels)}
    pc_df['tactical_label'] = pc_df['label'].map(legend_mapping)

    # Create a 2-panel figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    fig.suptitle('K-Medoids Dogfight Archetype Analysis', fontsize=20)

    # --- Panel 1: 2D PCA Scatter Plot ---
    sns.scatterplot(x='PC 1', y='PC 2', hue='tactical_label', data=pc_df, palette='viridis', ax=ax1, alpha=0.7)
    ax1.scatter(medoid_pcs[:, 0], medoid_pcs[:, 1], s=250, c='red', marker='*', label='Medoids', zorder=5)
    ax1.set_title('PCA of Discovered Flight Clusters', fontsize=16)
    ax1.legend(title='Tactical Archetype')
    ax1.grid(True)

    # --- Panel 2: Radar Chart of Medoids ---
    angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
    angles += angles[:1] # complete the loop

    ax2 = plt.subplot(1, 2, 2, polar=True)
    
    for i, medoid in enumerate(medoids):
        values = np.concatenate((medoid, medoid[:1]))
        ax2.plot(angles, values, linewidth=2, linestyle='solid', label=f'Medoid {i}: {tactical_labels[i]}')
        ax2.fill(angles, values, alpha=0.25)

    ax2.set_thetagrids(np.degrees(angles[:-1]))
    ax2.set_xticklabels(features)
    ax2.set_title('Medoid Feature Comparison', fontsize=16)
    ax2.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

    # Save the figure
    plt.tight_layout()
    fig.subplots_adjust(top=0.9)
    plt.savefig(output_path)
    print(f"Visualization dashboard saved to {output_path}")

def infer_tactical_state(medoid_features):
    """Infers a tactical state based on key feature values."""
    # Example logic: High energy and low distance might be offensive
    if medoid_features['specific_energy_ratio'] > 0.6 and medoid_features['delta_distance'] < 0.4:
        return "High-Energy Offensive"
    elif medoid_features['specific_energy_ratio'] < 0.4:
        return "Low-Energy Defensive"
    else:
        return "Neutral/Transitional"

if __name__ == '__main__':
    try:
        df = pd.read_csv("data/processed/features.csv")
        labels = np.loadtxt("data/processed/labels.txt", dtype=int)
        medoids = np.loadtxt("data/processed/medoids.txt")
    except FileNotFoundError:
        print("Error: Processed data or clustering results not found.")
        exit()

    features = [
        'delta_distance', 'angle_off_tail', 'antenna_train_angle', 
        'closure_rate', 'delta_altitude', 'specific_energy_ratio', 
        'energy_bleed_rate', 'relative_pitch_angle', 'relative_roll_angle', 
        'delta_load_factor'
    ]

    output_file = "visualizations/cluster_dashboard.png"
    tactical_labels = [infer_tactical_state(dict(zip(features, medoid))) for medoid in medoids]
    create_visualization_dashboard(df, labels, medoids, features, output_file, tactical_labels)
