# K-Medoids Cluster Analysis Report

This report details the tactical archetypes discovered by the K-Medoids clustering algorithm.

## Cluster 0: Neutral/Transitional

This cluster represents a distinct tactical state characterized by the following features:

| Feature                 | Normalized Value | Tactical Interpretation                                  |
|-------------------------|------------------|----------------------------------------------------------|
| delta_distance          | 0.3712           | Close range, offensive or defensive maneuvers are critical. |
| angle_off_tail          | 0.7290           | Neutral or defensive position, not behind the opponent. |
| antenna_train_angle     | 0.6020           | Opponent is off-boresight, but within sensor range. |
| closure_rate            | 0.2534           | Increasing distance, likely disengaging.         |
| delta_altitude          | 0.2574           | Aircraft are co-altitude.                        |
| specific_energy_ratio   | 0.4490           | Relatively neutral energy state.                 |
| energy_bleed_rate       | 0.4137           | Energy states are changing at a similar rate.    |
| relative_pitch_angle    | 0.5284           | Moderate difference in pitch.                    |
| relative_roll_angle     | 0.3326           | Moderate difference in roll.                     |
| delta_load_factor       | 0.0967           | Aircraft are maneuvering with similar G-forces.  |

## Cluster 1: High-Energy Offensive

This cluster represents a distinct tactical state characterized by the following features:

| Feature                 | Normalized Value | Tactical Interpretation                                  |
|-------------------------|------------------|----------------------------------------------------------|
| delta_distance          | 0.3106           | Close range, offensive or defensive maneuvers are critical. |
| angle_off_tail          | 0.6479           | Advantageous position, slightly off the opponent's tail. |
| antenna_train_angle     | 0.3795           | Opponent is off-boresight, but within sensor range. |
| closure_rate            | 0.4966           | Maintaining distance, likely a neutral or turning fight. |
| delta_altitude          | 0.2803           | Aircraft are co-altitude.                        |
| specific_energy_ratio   | 0.7518           | Significant energy advantage over the opponent.  |
| energy_bleed_rate       | 0.7544           | Losing energy much faster than the opponent.     |
| relative_pitch_angle    | 0.2145           | Aircraft are pointing in a similar vertical direction. |
| relative_roll_angle     | 0.0189           | Aircraft have a similar roll angle (lift vectors aligned). |
| delta_load_factor       | 0.2551           | Aircraft are maneuvering with similar G-forces.  |

## Cluster 2: Low-Energy Defensive

This cluster represents a distinct tactical state characterized by the following features:

| Feature                 | Normalized Value | Tactical Interpretation                                  |
|-------------------------|------------------|----------------------------------------------------------|
| delta_distance          | 0.7383           | Long range, likely in a neutral or search phase. |
| angle_off_tail          | 0.2390           | Directly behind the opponent, in a high-success position. |
| antenna_train_angle     | 0.2249           | Opponent is directly in front, on-boresight.     |
| closure_rate            | 0.8770           | Rapidly closing distance, likely an attack run.  |
| delta_altitude          | 0.5994           | Moderate altitude difference.                    |
| specific_energy_ratio   | 0.2814           | Significant energy disadvantage.                 |
| energy_bleed_rate       | 0.5234           | Energy states are changing at a similar rate.    |
| relative_pitch_angle    | 0.1621           | Aircraft are pointing in a similar vertical direction. |
| relative_roll_angle     | 0.2960           | Aircraft have a similar roll angle (lift vectors aligned). |
| delta_load_factor       | 0.0543           | Aircraft are maneuvering with similar G-forces.  |

