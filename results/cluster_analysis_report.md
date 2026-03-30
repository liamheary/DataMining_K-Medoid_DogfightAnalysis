# K-Medoids Cluster Analysis Report

This report details the tactical archetypes discovered by the K-Medoids clustering algorithm.

## Cluster 0: Neutral/Transitional

This cluster represents a distinct tactical state characterized by the following features:

| Feature                 | Normalized Value | Tactical Interpretation                                  |
|-------------------------|------------------|----------------------------------------------------------|
| delta_distance          | 0.4389           | Close range, offensive or defensive maneuvers are critical. |
| angle_off_tail          | 0.4699           | Advantageous position, slightly off the opponent's tail. |
| antenna_train_angle     | 0.1275           | Opponent is directly in front, on-boresight.     |
| closure_rate            | 0.7093           | Rapidly closing distance, likely an attack run.  |
| delta_altitude          | 0.6477           | Moderate altitude difference.                    |
| specific_energy_ratio   | 0.5703           | Relatively neutral energy state.                 |
| energy_bleed_rate       | 0.7424           | Losing energy much faster than the opponent.     |
| relative_pitch_angle    | 0.1049           | Aircraft are pointing in a similar vertical direction. |
| relative_roll_angle     | 0.4586           | Moderate difference in roll.                     |
| delta_load_factor       | 0.2744           | Aircraft are maneuvering with similar G-forces.  |

## Cluster 1: Low-Energy Defensive

This cluster represents a distinct tactical state characterized by the following features:

| Feature                 | Normalized Value | Tactical Interpretation                                  |
|-------------------------|------------------|----------------------------------------------------------|
| delta_distance          | 0.6745           | Close range, offensive or defensive maneuvers are critical. |
| angle_off_tail          | 0.6511           | Advantageous position, slightly off the opponent's tail. |
| antenna_train_angle     | 0.5283           | Opponent is off-boresight, but within sensor range. |
| closure_rate            | 0.3211           | Maintaining distance, likely a neutral or turning fight. |
| delta_altitude          | 0.4575           | Moderate altitude difference.                    |
| specific_energy_ratio   | 0.3110           | Relatively neutral energy state.                 |
| energy_bleed_rate       | 0.3738           | Energy states are changing at a similar rate.    |
| relative_pitch_angle    | 0.0328           | Aircraft are pointing in a similar vertical direction. |
| relative_roll_angle     | 0.5516           | Moderate difference in roll.                     |
| delta_load_factor       | 0.3765           | Moderate difference in G-loading.                |

## Cluster 2: Low-Energy Defensive

This cluster represents a distinct tactical state characterized by the following features:

| Feature                 | Normalized Value | Tactical Interpretation                                  |
|-------------------------|------------------|----------------------------------------------------------|
| delta_distance          | 0.2577           | Extremely close range, merge has likely occurred. |
| angle_off_tail          | 0.6190           | Advantageous position, slightly off the opponent's tail. |
| antenna_train_angle     | 0.5039           | Opponent is off-boresight, but within sensor range. |
| closure_rate            | 0.3463           | Maintaining distance, likely a neutral or turning fight. |
| delta_altitude          | 0.0827           | Aircraft are co-altitude.                        |
| specific_energy_ratio   | 0.2646           | Significant energy disadvantage.                 |
| energy_bleed_rate       | 0.5486           | Energy states are changing at a similar rate.    |
| relative_pitch_angle    | 0.2925           | Aircraft are pointing in a similar vertical direction. |
| relative_roll_angle     | 0.3508           | Moderate difference in roll.                     |
| delta_load_factor       | 0.5411           | Moderate difference in G-loading.                |

