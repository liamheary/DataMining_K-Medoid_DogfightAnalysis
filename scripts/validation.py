
import numpy as np
from src.data_generator import DogfightEnvironment

def run_validation(medoid):
    env = DogfightEnvironment()
    # This is a placeholder for setting the initial state of the simulation
    # to the medoid state. In a real scenario, this would involve a more
    # complex process of converting the medoid features back into a
    # simulation state.
    print(f"Running validation for medoid: {medoid}")
    state_a, state_b = env.reset()
    env.render()

    # Run the simulation for a fixed number of steps and see if the AI survives
    for _ in range(1000):
        action_a = env.get_simple_action(state_a, state_b)
        action_b = env.get_simple_action(state_b, state_a)
        
        (state_a, state_b), _, done, _, winner, loser = env.step(action_a, action_b)
        env.render()
        
        if done:
            print(f"AI survived for {_} steps.")
            break

if __name__ == '__main__':
    # Load the medoids
    try:
        medoids = np.loadtxt("data/processed/medoids.txt")
    except FileNotFoundError:
        print("Error: Medoids not found. Please run the kmedoids script first.")
        exit()

    # Run the validation for each medoid
    for medoid in medoids:
        run_validation(medoid)
