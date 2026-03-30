
import jsbsim
import gymnasium as gym
import numpy as np
import pandas as pd
import os
from datetime import datetime

def geodetic_to_ecef(lat, lon, alt):
    """Converts geodetic coordinates to ECEF coordinates."""
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    a = 6378137.0  # WGS-84 Earth semi-major axis in meters
    e2 = 6.69437999014e-3  # WGS-84 first eccentricity squared
    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)
    
    x = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
    y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
    z = ((1 - e2) * N + alt) * np.sin(lat_rad)
    return x, y, z

class DogfightEnvironment(gym.Env):
    def __init__(self, fdm_hz=240, sim_hz=60, agent_interaction_step=0.1):
        super().__init__()
        self.fdm_hz = fdm_hz
        self.sim_hz = sim_hz
        self.agent_interaction_step = agent_interaction_step
        self.telemetry_buffer = []

        self.jsbsim_exec_a = jsbsim.FGFDMExec(root_dir=".")
        self.jsbsim_exec_b = jsbsim.FGFDMExec(root_dir=".")
        self.jsbsim_exec_a.load_model("f16")
        self.jsbsim_exec_b.load_model("f16")

        self._set_initial_conditions()

    def _set_initial_conditions(self):
        # Initial conditions for Aircraft A
        self.jsbsim_exec_a["ic/u-fps"] = 800
        self.jsbsim_exec_a["ic/v-fps"] = 0
        self.jsbsim_exec_a["ic/w-fps"] = 0
        self.jsbsim_exec_a["ic/h-sl-ft"] = 20000
        self.jsbsim_exec_a["ic/lat-gc-deg"] = 34.0522
        self.jsbsim_exec_a["ic/long-gc-deg"] = -118.2437
        self.jsbsim_exec_a["ic/psi-true-deg"] = 90

        # Initial conditions for Aircraft B
        self.jsbsim_exec_b["ic/u-fps"] = 800
        self.jsbsim_exec_b["ic/v-fps"] = 0
        self.jsbsim_exec_b["ic/w-fps"] = 0
        self.jsbsim_exec_b["ic/h-sl-ft"] = 20000
        self.jsbsim_exec_b["ic/lat-gc-deg"] = 34.0522
        self.jsbsim_exec_b["ic/long-gc-deg"] = -118.2537
        self.jsbsim_exec_b["ic/psi-true-deg"] = -90

    def get_simple_action(self, state, opponent_state):
        # A simple AI that tries to turn towards the opponent
        delta_heading = opponent_state["heading"] - state["heading"]
        if delta_heading > 180:
            delta_heading -= 360
        if delta_heading < -180:
            delta_heading += 360
        
        action = {
            "aileron": np.clip(delta_heading / 180.0, -1.0, 1.0),
            "elevator": 0.0,
            "rudder": 0.0,
            "throttle": 1.0,
        }
        return action

    def step(self, action_a, action_b):
        # Apply actions to the simulation
        if action_a:
            self.jsbsim_exec_a["fcs/aileron-cmd-norm"] = action_a["aileron"]
            self.jsbsim_exec_a["fcs/elevator-cmd-norm"] = action_a["elevator"]
            self.jsbsim_exec_a["fcs/rudder-cmd-norm"] = action_a["rudder"]
            self.jsbsim_exec_a["propulsion/engine[0]/throttle-cmd-norm"] = action_a["throttle"]
        if action_b:
            self.jsbsim_exec_b["fcs/aileron-cmd-norm"] = action_b["aileron"]
            self.jsbsim_exec_b["fcs/elevator-cmd-norm"] = action_b["elevator"]
            self.jsbsim_exec_b["fcs/rudder-cmd-norm"] = action_b["rudder"]
            self.jsbsim_exec_b["propulsion/engine[0]/throttle-cmd-norm"] = action_b["throttle"]

        self.jsbsim_exec_a.run()
        self.jsbsim_exec_b.run()

        state_a = self._get_state(self.jsbsim_exec_a, 'A')
        state_b = self._get_state(self.jsbsim_exec_b, 'B')
        self.telemetry_buffer.append((state_a, state_b))

        # Buffer last 60 seconds of data
        if len(self.telemetry_buffer) > 60 * self.sim_hz:
            self.telemetry_buffer.pop(0)

        done, winner, loser = self._check_terminal_state(state_a, state_b)
        reward_a, reward_b = self._calculate_reward(state_a, state_b)
        info = {}

        return (state_a, state_b), (reward_a, reward_b), done, info, winner, loser

    def _calculate_reward(self, state_a, state_b):
        # A simple reward function based on relative angle and distance
        x_a, y_a, z_a = geodetic_to_ecef(state_a['latitude'], state_a['longitude'], state_a['altitude'])
        x_b, y_b, z_b = geodetic_to_ecef(state_b['latitude'], state_b['longitude'], state_b['altitude'])

        pos_a = np.array([x_a, y_a, z_a])
        pos_b = np.array([x_b, y_b, z_b])

        heading_a_rad = np.radians(state_a['heading'])
        heading_b_rad = np.radians(state_b['heading'])
        vel_a = state_a['airspeed'] * np.array([np.sin(heading_a_rad), np.cos(heading_a_rad), 0])
        vel_b = state_b['airspeed'] * np.array([np.sin(heading_b_rad), np.cos(heading_b_rad), 0])

        los_ab = pos_b - pos_a
        tail_b = -vel_b
        aot_rad = np.arccos(np.dot(tail_b, los_ab) / (np.linalg.norm(tail_b) * np.linalg.norm(los_ab)))
        angle_off_tail = np.degrees(aot_rad)

        distance = np.linalg.norm(los_ab)

        # Reward for being in a good position (behind the opponent)
        reward_a = (180 - angle_off_tail) / 180.0 - distance / 50000.0
        reward_b = -reward_a

        return reward_a, reward_b

    def _get_state(self, fdm_exec, aircraft_id):
        return {
            "aircraft_id": aircraft_id,
            "timestamp": datetime.now(),
            "altitude": fdm_exec["position/h-sl-ft"],
            "latitude": fdm_exec["position/lat-gc-deg"],
            "longitude": fdm_exec["position/long-gc-deg"],
            "airspeed": fdm_exec["velocities/v-true-fps"],
            "heading": fdm_exec["attitude/psi-deg"],
            "pitch": np.degrees(fdm_exec["attitude/theta-rad"]),
            "roll": np.degrees(fdm_exec["attitude/phi-rad"]),
            "load_factor": fdm_exec["accelerations/nz-pilot-g"],
        }

    def _check_terminal_state(self, state_a, state_b):
        # Rule-based terminal state detection
        # 1. Crash detection
        if state_a["altitude"] < 0 or state_b["altitude"] < 0:
            winner = 'B' if state_a["altitude"] < 0 else 'A'
            loser = 'A' if state_a["altitude"] < 0 else 'B'
            return True, winner, loser

        # 2. Collision detection
        lat_a, lon_a, alt_a = state_a['latitude'], state_a['longitude'], state_a['altitude']
        lat_b, lon_b, alt_b = state_b['latitude'], state_b['longitude'], state_b['altitude']
        
        x_a, y_a, z_a = geodetic_to_ecef(lat_a, lon_a, alt_a)
        x_b, y_b, z_b = geodetic_to_ecef(lat_b, lon_b, alt_b)
        
        distance = np.linalg.norm(np.array([x_a, y_a, z_a]) - np.array([x_b, y_b, z_b]))
        
        if distance < 100: # 100 feet
            # For simplicity, assume a tie and randomly assign winner/loser
            winner, loser = ('A', 'B') if np.random.rand() < 0.5 else ('B', 'A')
            return True, winner, loser

        return False, None, None

    def reset(self):
        self.telemetry_buffer = []
        self._set_initial_conditions()
        self.jsbsim_exec_a.run()
        self.jsbsim_exec_b.run()
        return self._get_state(self.jsbsim_exec_a, 'A'), self._get_state(self.jsbsim_exec_b, 'B')

    def render(self, mode='human'):
        state_a = self._get_state(self.jsbsim_exec_a, 'A')
        state_b = self._get_state(self.jsbsim_exec_b, 'B')
        print(f"Aircraft A: {state_a}")
        print(f"Aircraft B: {state_b}")

    def save_telemetry(self, winner, loser):
        # Create a DataFrame from the telemetry buffer
        df = pd.DataFrame([frame for aircraft_frames in self.telemetry_buffer for frame in aircraft_frames])
        
        # Label the data
        df["label"] = np.where(df["aircraft_id"] == winner, "High-Success", "High-Threat")
        
        # Save to a CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/raw/dogfight_{timestamp}.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Telemetry data saved to {output_path}")

import tqdm

if __name__ == "__main__":
    TARGET_SIMULATIONS = 500
    env = DogfightEnvironment()
    
    with tqdm.tqdm(total=TARGET_SIMULATIONS, desc="Generating Simulation Data") as pbar:
        simulations_run = 0
        while simulations_run < TARGET_SIMULATIONS:
            state_a, state_b = env.reset()
            for _ in range(1000):  # Max steps per simulation
                action_a = env.get_simple_action(state_a, state_b)
                action_b = env.get_simple_action(state_b, state_a)
                
                (state_a, state_b), _, done, _, winner, loser = env.step(action_a, action_b)
                
                if done:
                    env.save_telemetry(winner, loser)
                    simulations_run += 1
                    pbar.update(1)
                    break
