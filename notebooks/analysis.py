
import pandas as pd
import numpy as np

def analyze_clusters(df, labels, medoids, features):
    n_clusters = len(medoids)
    df['label'] = labels
    for i in range(n_clusters):
        cluster_df = df[df['label'] == i]
        print(f"\n--- Cluster {i} ---")
        print(f"Medoid: {medoids[i]}")
        print("\nAverage feature values:")
        print(cluster_df[features].mean())
        print("\nCluster characteristics:")
        # This is a placeholder for a more detailed analysis of the cluster characteristics.
        # In a real scenario, this would involve a deeper understanding of the features
        # and how they relate to air combat tactics.
        if cluster_df['specific_energy_ratio'].mean() > 0.6:
            print("This cluster represents a high-energy state.")
        else:
            print("This cluster represents a low-energy state.")

if __name__ == '__main__':
    # Load the processed data and the results of the clustering
    try:
        df = pd.read_csv("data/processed/features.csv")
        labels = np.loadtxt("data/processed/labels.txt")
        medoids = np.loadtxt("data/processed/medoids.txt")
    except FileNotFoundError:
        print("Error: Processed data or clustering results not found. Please run the feature engineering and kmedoids scripts first.")
        exit()

    # Select the features to use for clustering
    features = [
        'delta_distance', 'angle_off_tail', 'antenna_train_angle', 
        'closure_rate', 'delta_altitude', 'specific_energy_ratio', 
        'energy_bleed_rate', 'relative_pitch_angle', 'relative_roll_angle', 
        'delta_load_factor'
    ]

    analyze_clusters(df, labels, medoids, features)
