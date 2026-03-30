
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, davies_bouldin_score
import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds to run.")
        return result
    return wrapper

class KMedoids:
    def __init__(self, n_clusters, max_iter=100, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state

    def _manhattan_distance(self, a, b):
        return np.sum(np.abs(a - b), axis=1)

    @timing_decorator
    def fit(self, X):
        # 1. Initialize medoids
        np.random.seed(self.random_state)
        initial_medoid_indices = np.random.choice(len(X), self.n_clusters, replace=False)
        self.medoids_ = X[initial_medoid_indices]

        for i in range(self.max_iter):
            # 2. Assign clusters
            distances = np.zeros((len(X), self.n_clusters))
            for k in range(self.n_clusters):
                distances[:, k] = self._manhattan_distance(X, self.medoids_[k])
            
            self.labels_ = np.argmin(distances, axis=1)

            # 3. Update medoids
            new_medoids = self.medoids_.copy()
            for k in range(self.n_clusters):
                cluster_points = X[self.labels_ == k]
                if len(cluster_points) > 0:
                    # Calculate the cost for each point in the cluster
                    costs = np.sum([self._manhattan_distance(p, cluster_points) for p in cluster_points], axis=0)
                    
                    # Find the point with the minimum cost
                    new_medoid_index = np.argmin(costs)
                    new_medoids[k] = cluster_points[new_medoid_index]

            # Check for convergence
            if np.all(new_medoids == self.medoids_):
                break
            
            self.medoids_ = new_medoids

        return self

if __name__ == '__main__':
    # Load the processed data
    try:
        df = pd.read_csv("data/processed/features.csv")
    except FileNotFoundError:
        print("Error: Processed data file not found. Please run the feature engineering script first.")
        exit()

    # Select the features to use for clustering
    features = [
        'delta_distance', 'angle_off_tail', 'antenna_train_angle', 
        'closure_rate', 'delta_altitude', 'specific_energy_ratio', 
        'energy_bleed_rate', 'relative_pitch_angle', 'relative_roll_angle', 
        'delta_load_factor'
    ]
    X = df[features].values

    # Create a KMedoids instance and fit the data
    kmedoids = KMedoids(n_clusters=3, random_state=42)
    kmedoids.fit(X)

    # Print the results
    print("Medoids:")
    print(kmedoids.medoids_)
    print("\nLabels:")
    print(kmedoids.labels_)

    # Calculate and print the evaluation metrics
    silhouette = silhouette_score(X, kmedoids.labels_)
    davies_bouldin = davies_bouldin_score(X, kmedoids.labels_)

    print(f"\nSilhouette Coefficient: {silhouette}")
    print(f"Davies-Bouldin Index: {davies_bouldin}")

    # Save the labels and medoids to files
    np.savetxt("data/processed/labels.txt", kmedoids.labels_, fmt="%d")
    np.savetxt("data/processed/medoids.txt", kmedoids.medoids_)
