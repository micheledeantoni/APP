import pandas as pd
import numpy as np

def find_closest_players(player_index, raw_data, compressed_data):
    '''
    player index, raw_data as a Dataframe, compressed_data as a numpy array
    function that prints out the 5 closest player to the selected one
    '''

    # Step 1: Choose a Player
    player_of_interest_index = player_index  # Replace with the index of the player you're interested in

    # Step 2: Get the Cluster Assignment of the Player of Interest
    cluster_of_interest = raw_data.loc[player_of_interest_index, 'label']

    # Step 3: Filter Data for the Same Cluster
    cluster_indices = np.where(raw_data['label'] == cluster_of_interest)[0]

    # Step 4: Calculate Distances
    distances = np.linalg.norm(compressed_data[cluster_indices] - compressed_data[player_of_interest_index], axis=1)

    # Step 5: Identify the 5 Closest Players
    closest_player_indices = cluster_indices[np.argsort(distances)[1:5]]
    closest_players = raw_data.iloc[closest_player_indices]

    print(f"The closest player to the player of interest is:\n{closest_players['long_name']}")
