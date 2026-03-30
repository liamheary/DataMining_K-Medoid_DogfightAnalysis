
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

def create_visualization_dashboard(df, labels, medoids, features, output_path):
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
    tactical_labels = [infer_tactical_state(dict(zip(features, medoid))) for medoid in medoids]
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

    ax2.set_thetagrids(np.degrees(angles[:-1]), features)
    ax2.set_title('Medoid Feature Comparison', fontsize=16)
    ax2.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

    # Save the figure
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path)
    print(f"Visualization dashboard saved to {output_path}")

def generate_markdown_report(medoids, features, tactical_labels, report_path):
    """Generates a Markdown report summarizing the cluster analysis."""
    with open(report_path, 'w') as f:
        f.write("# K-Medoids Cluster Analysis Report\n\n")
        f.write("This report details the tactical archetypes discovered by the K-Medoids clustering algorithm.\n\n")

        for i, medoid in enumerate(medoids):
            f.write(f"## Cluster {i}: {tactical_labels[i]}\n\n")
            f.write("This cluster represents a distinct tactical state characterized by the following features:\n\n")
            f.write("| Feature                 | Normalized Value | Tactical Interpretation                                  |\n")
            f.write("|-------------------------|------------------|----------------------------------------------------------|\n")

            for j, feature_name in enumerate(features):
                value = medoid[j]
                interpretation = get_feature_interpretation(feature_name, value)
                f.write(f"| {feature_name:<23} | {value:<16.4f} | {interpretation:<48} |\n")
            f.write("\n")

def get_feature_interpretation(feature_name, value):
    """Provides a qualitative interpretation of a normalized feature value."""
    interpretations = {
        'delta_distance': {
            "high": "Long range, likely in a neutral or search phase.",
            "medium": "Close range, offensive or defensive maneuvers are critical.",
            "low": "Extremely close range, merge has likely occurred."
        },
        'specific_energy_ratio': {
            "high": "Significant energy advantage over the opponent.",
            "medium": "Relatively neutral energy state.",
            "low": "Significant energy disadvantage."
        },
        'angle_off_tail': {
            "high": "Neutral or defensive position, not behind the opponent.",
            "medium": "Advantageous position, slightly off the opponent's tail.",
            "low": "Directly behind the opponent, in a high-success position."
        },
        'closure_rate': {
            "high": "Rapidly closing distance, likely an attack run.",
            "medium": "Maintaining distance, likely a neutral or turning fight.",
            "low": "Increasing distance, likely disengaging."
        },
        'delta_altitude': {
            "high": "Significant altitude advantage or disadvantage.",
            "medium": "Moderate altitude difference.",
            "low": "Aircraft are co-altitude."
        },
        'energy_bleed_rate': {
            "high": "Losing energy much faster than the opponent.",
            "medium": "Energy states are changing at a similar rate.",
            "low": "Gaining energy much faster than the opponent."
        },
        'relative_pitch_angle': {
            "high": "Aircraft are pointing in very different vertical directions.",
            "medium": "Moderate difference in pitch.",
            "low": "Aircraft are pointing in a similar vertical direction."
        },
        'relative_roll_angle': {
            "high": "Aircraft are rolled to very different angles.",
            "medium": "Moderate difference in roll.",
            "low": "Aircraft have a similar roll angle (lift vectors aligned)."
        },
        'delta_load_factor': {
            "high": "One aircraft is maneuvering much harder than the other.",
            "medium": "Moderate difference in G-loading.",
            "low": "Aircraft are maneuvering with similar G-forces."
        },
        'antenna_train_angle': {
            "high": "Opponent is far off-boresight, requiring a large turn to engage.",
            "medium": "Opponent is off-boresight, but within sensor range.",
            "low": "Opponent is directly in front, on-boresight."
        }
    }

    if feature_name in interpretations:
        if value > 0.7:
            return interpretations[feature_name]["high"]
        elif value > 0.3:
            return interpretations[feature_name]["medium"]
        else:
            return interpretations[feature_name]["low"]
    return "(Interpretation not available)"

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
    create_visualization_dashboard(df, labels, medoids, features, output_file)

    report_file = "data/processed/cluster_analysis_report.md"
    tactical_labels = [infer_tactical_state(dict(zip(features, medoid))) for medoid in medoids]
    generate_markdown_report(medoids, features, tactical_labels, report_file)
    print(f"Analysis report saved to {report_file}")
