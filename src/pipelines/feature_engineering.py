
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

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

def calculate_specific_energy(altitude, airspeed):
    """Calculates the specific energy of an aircraft."""
    g = 32.174  # acceleration due to gravity in ft/s^2
    return altitude + (airspeed**2 / (2 * g))

def calculate_relative_features(df):
    """
    Calculates the 10 relative features between two aircraft for each frame.
    """
    
    # Group by timestamp to process each frame
    grouped = df.groupby('timestamp')
    
    # Create a new DataFrame to store the relative features
    relative_df = pd.DataFrame()

    # Initialize previous energy values
    prev_Es = {}

    for timestamp, group in grouped:
        if len(group) == 2:
            # Ensure we have data for both aircraft
            group = group.set_index('aircraft_id')
            
            # --- DELTA ALTITUDE ---
            delta_altitude = abs(group.loc['A']['altitude'] - group.loc['B']['altitude'])
            
            # --- DELTA DISTANCE (3D) ---
            lat1_rad = np.radians(group.loc['A']['latitude'])
            lon1_rad = np.radians(group.loc['A']['longitude'])
            lat2_rad = np.radians(group.loc['B']['latitude'])
            lon2_rad = np.radians(group.loc['B']['longitude'])
            
            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad
            a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            ground_distance_ft = 3959 * 5280 * c
            
            delta_distance = np.sqrt(ground_distance_ft**2 + delta_altitude**2)

            # --- VECTOR CALCULATIONS for AOT and ATA ---
            x_a, y_a, z_a = geodetic_to_ecef(group.loc['A']['latitude'], group.loc['A']['longitude'], group.loc['A']['altitude'])
            x_b, y_b, z_b = geodetic_to_ecef(group.loc['B']['latitude'], group.loc['B']['longitude'], group.loc['B']['altitude'])
            
            pos_a = np.array([x_a, y_a, z_a])
            pos_b = np.array([x_b, y_b, z_b])

            heading_a_rad = np.radians(group.loc['A']['heading'])
            heading_b_rad = np.radians(group.loc['B']['heading'])
            vel_a = group.loc['A']['airspeed'] * np.array([np.sin(heading_a_rad), np.cos(heading_a_rad), 0])
            vel_b = group.loc['B']['airspeed'] * np.array([np.sin(heading_b_rad), np.cos(heading_b_rad), 0])

            los_ab = pos_b - pos_a

            # --- ANGLE OFF TAIL (AOT) ---
            tail_b = -vel_b
            aot_rad = np.arccos(np.dot(tail_b, los_ab) / (np.linalg.norm(tail_b) * np.linalg.norm(los_ab)))
            angle_off_tail = np.degrees(aot_rad)

            # --- ANTENNA TRAIN ANGLE (ATA) ---
            nose_a = vel_a
            ata_rad = np.arccos(np.dot(nose_a, los_ab) / (np.linalg.norm(nose_a) * np.linalg.norm(los_ab)))
            antenna_train_angle = np.degrees(ata_rad)

            # --- CLOSURE RATE (Vc) ---
            vel_rel = vel_b - vel_a
            closure_rate = -np.dot(vel_rel, los_ab) / np.linalg.norm(los_ab)

            # --- ENERGY-BASED FEATURES ---
            Es_a = calculate_specific_energy(group.loc['A']['altitude'], group.loc['A']['airspeed'])
            Es_b = calculate_specific_energy(group.loc['B']['altitude'], group.loc['B']['airspeed'])
            
            specific_energy_ratio = Es_a / Es_b
            
            time_delta = (timestamp - prev_Es.get('timestamp', timestamp)).total_seconds()
            if time_delta > 0:
                energy_bleed_rate_a = (Es_a - prev_Es.get('Es_a', Es_a)) / time_delta
                energy_bleed_rate_b = (Es_b - prev_Es.get('Es_b', Es_b)) / time_delta
            else:
                energy_bleed_rate_a = 0
                energy_bleed_rate_b = 0
            
            energy_bleed_rate = energy_bleed_rate_a - energy_bleed_rate_b

            prev_Es['Es_a'] = Es_a
            prev_Es['Es_b'] = Es_b
            prev_Es['timestamp'] = timestamp

            # --- ATTITUDE FEATURES ---
            relative_pitch_angle = abs(group.loc['A']['pitch'] - group.loc['B']['pitch'])
            relative_roll_angle = abs(group.loc['A']['roll'] - group.loc['B']['roll'])

            # --- DELTA LOAD FACTOR ---
            delta_load_factor = abs(group.loc['A']['load_factor'] - group.loc['B']['load_factor'])

            relative_features = {
                'timestamp': timestamp,
                'delta_distance': delta_distance,
                'delta_altitude': delta_altitude,
                'angle_off_tail': angle_off_tail,
                'antenna_train_angle': antenna_train_angle,
                'closure_rate': closure_rate,
                'specific_energy_ratio': specific_energy_ratio,
                'energy_bleed_rate': energy_bleed_rate,
                'relative_pitch_angle': relative_pitch_angle,
                'relative_roll_angle': relative_roll_angle,
                'delta_load_factor': delta_load_factor
            }
            relative_df = pd.concat([relative_df, pd.DataFrame([relative_features])], ignore_index=True)

    return relative_df

def normalize_features(df):
    scaler = MinMaxScaler()
    features = [
        'delta_distance', 'angle_off_tail', 'antenna_train_angle', 
        'closure_rate', 'delta_altitude', 'specific_energy_ratio', 
        'energy_bleed_rate', 'relative_pitch_angle', 'relative_roll_angle', 
        'delta_load_factor'
    ]
    df[features] = scaler.fit_transform(df[features])
    return df

if __name__ == "__main__":
    # This is a placeholder for loading the raw data.
    # In a real scenario, this would load the CSV files from the data/raw directory.
    
    # Create a dummy dataframe for demonstration purposes
    data = {
        'aircraft_id': ['A', 'B'] * 50,
        'timestamp': np.repeat(pd.to_datetime(np.arange(50), unit='s'), 2),
        'altitude': np.random.uniform(15000, 25000, 100),
        'latitude': np.random.uniform(34, 35, 100),
        'longitude': np.random.uniform(-118, -119, 100),
        'airspeed': np.random.uniform(700, 900, 100),
        'heading': np.random.uniform(0, 360, 100),
        'pitch': np.random.uniform(-90, 90, 100),
        'roll': np.random.uniform(-180, 180, 100),
        'load_factor': np.random.uniform(1, 9, 100),
    }
    df = pd.DataFrame(data)

    # Calculate relative features
    relative_df = calculate_relative_features(df)
    
    # Normalize features
    normalized_df = normalize_features(relative_df.copy())
    
    # Save the processed data
    normalized_df.to_csv("data/processed/features.csv", index=False)
    
    print("Feature engineering complete. Processed data saved to data/processed/features.csv")
