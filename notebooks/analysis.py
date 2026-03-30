
import pandas as pd
import numpy as np
import sys
sys.path.append('.')
from src.pipelines.visualization import create_visualization_dashboard, create_kde_plot

def infer_tactical_state(medoid_features):
    """Infers a tactical state based on key feature values."""
    # Example logic: High energy and low distance might be offensive
    if medoid_features['specific_energy_ratio'] > 0.6 and medoid_features['delta_distance'] < 0.4:
        return "Archetype A: The High-Energy Advantage"
    elif medoid_features['specific_energy_ratio'] < 0.4:
        return "Archetype B: The Defensive Death Spiral"
    else:
        return "Archetype C: Neutral/Transitional"

def generate_markdown_report(medoids, features, tactical_labels, report_path, num_simulations):
    """Generates a comprehensive Markdown report summarizing the cluster analysis."""
    with open(report_path, 'w') as f:
        # 1. Executive Summary
        f.write("# K-Medoids Dogfight Analysis: Tactical Archetype Report\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(f"This report details the results of a data mining analysis performed on a dataset of **{num_simulations}+ simulated 1-vs-1 F-16 engagements**. ")
        f.write("Using a custom-built K-Medoids clustering algorithm, we have identified three distinct, recurring tactical archetypes from the flight telemetry. ")
        f.write("These archetypes represent common, physically-realizable states in air combat that correspond to conditions of advantage, disadvantage, and neutrality.")
        f.write("\n\n---\n\n")

        # 2. Methodology Overview
        f.write("## 2. Methodology Overview\n\n")
        f.write("The core of this analysis is the **K-Medoids (Partitioning Around Medoids - PAM)** algorithm. Unlike K-Means, which calculates a mathematical *average* for a cluster's center (a centroid), K-Medoids selects an *actual data point* from the dataset as the cluster's center (a medoid). ")
        f.write("This is critical for our application, as it ensures that each tactical archetype is represented by a physically possible flight state that occurred in the simulation.\n\n")
        f.write("**Manhattan Distance** was chosen as the distance metric. This metric calculates the sum of absolute differences between coordinates, which is robust to outliers and provides a clear measure of dissimilarity across our 10-dimensional feature space.\n\n")
        f.write("![Visualization Dashboard](../visualizations/cluster_dashboard.png)\n*Caption: A 2D PCA projection of the clusters and a radar chart comparing medoid features.*")
        f.write("\n\n---\n\n")

        # 3. The Discovered Archetypes
        f.write("## 3. The Discovered Archetypes\n\n")
        for i, medoid in enumerate(medoids):
            f.write(f"### {tactical_labels[i]}\n\n")
            
            # Tactical Summary
            if "Advantage" in tactical_labels[i]:
                f.write("**Tactical Summary:** This archetype represents a **position of significant advantage**. The aircraft in this state has a high energy level, is likely behind the opponent, and is in a prime position to dictate the terms of the engagement. This is a *High-Success* state to be sought after.\n\n")
            elif "Defensive" in tactical_labels[i]:
                f.write("**Tactical Summary:** This archetype represents a **defensive, high-threat situation**. The aircraft has a low energy state, is likely being targeted, and has limited options for offensive maneuvers. This is a *High-Threat* state to be avoided.\n\n")
            else:
                f.write("**Tactical Summary:** This archetype represents a **neutral or transitional state**. Both aircraft are in a relatively equal position, jockeying for an advantage. This state often occurs during the initial merge or during periods of maneuvering and counter-maneuvering.\n\n")

            # Feature Breakdown Table
            f.write("**Feature Breakdown:**\n\n")
            f.write("| Feature                 | Normalized Value | Tactical Interpretation                                  |\n")
            f.write("|-------------------------|------------------|----------------------------------------------------------|\n")
            for j, feature_name in enumerate(features):
                value = medoid[j]
                interpretation = get_feature_interpretation(feature_name, value)
                f.write(f"| {feature_name:<23} | {value:<16.4f} | {interpretation:<48} |\n")
            f.write("\n---\n\n")

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
    import subprocess
    subprocess.run(["python3", "src/pipelines/visualization.py"])

    # Generate Markdown Report
    report_file = "results/cluster_analysis_report.md"
    tactical_labels = [infer_tactical_state(dict(zip(features, medoid))) for medoid in medoids]
    generate_markdown_report(medoids, features, tactical_labels, report_file, 500)
    print(f"Analysis report saved to {report_file}")
