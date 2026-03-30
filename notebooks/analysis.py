
import pandas as pd
import numpy as np
import sys
sys.path.append('.')
from src.pipelines.visualization import create_visualization_dashboard, infer_tactical_state

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

    # Generate Visualization
    output_file = "visualizations/cluster_dashboard.png"
    tactical_labels = [infer_tactical_state(dict(zip(features, medoid))) for medoid in medoids]
    create_visualization_dashboard(df, labels, medoids, features, output_file, tactical_labels)

    # Generate Markdown Report
    report_file = "results/cluster_analysis_report.md"
    tactical_labels = [infer_tactical_state(dict(zip(features, medoid))) for medoid in medoids]
    generate_markdown_report(medoids, features, tactical_labels, report_file)
    print(f"Analysis report saved to {report_file}")

def infer_tactical_state(medoid_features):
    """Infers a tactical state based on key feature values."""
    # Example logic: High energy and low distance might be offensive
    if medoid_features['specific_energy_ratio'] > 0.6 and medoid_features['delta_distance'] < 0.4:
        return "High-Energy Offensive"
    elif medoid_features['specific_energy_ratio'] < 0.4:
        return "Low-Energy Defensive"
    else:
        return "Neutral/Transitional"
