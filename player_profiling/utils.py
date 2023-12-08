import pandas as pd
import numpy as np

def find_closest_players(player_index, raw_data, compressed_data):
    '''
    player index, raw_data as a Dataframe, compressed_data as a numpy array
    function that prints out the 5 closest player to the selected one
    '''
    # Step 0: Gives player name index based on user input
    #player_index = finding_player_index(player_name,raw_data)
    # Step 1: Choose a Player
    player_of_interest_index = player_index  # Replace with the index of the player you're interested in

    # Step 2: Get the Cluster Assignment of the Player of Interest
    cluster_of_interest = raw_data.loc[player_of_interest_index, 'label']

    # Step 3: Filter Data for the Same Cluster
    cluster_indices = np.where(raw_data['label'] == cluster_of_interest)[0]

    compressed_data = pd.DataFrame(compressed_data).drop(columns=['idx'])
    # Step 4: Calculate Distances
    distances = np.linalg.norm(compressed_data.iloc[cluster_indices].values -
                               compressed_data.iloc[player_of_interest_index].values, axis=1)

    # Step 5: Identify the 5 Closest Players
    closest_player_indices = cluster_indices[np.argsort(distances)[1:6]]
    closest_players = raw_data.iloc[closest_player_indices]

    #print(f"The closest player to the player of interest is:\n{closest_players['short_name']}")

    return closest_players['short_name']


def find_player_match (name, data):

    matched_names = []
    name = name.upper()

    for sn, ln in zip(data['short_name'], data['long_name']):
        snc = sn.upper()
        lnc = ln.upper()
        if name in snc:
            matched_names.append(sn)
        elif name in lnc:
             matched_names.append(sn)

    return matched_names


def find_player_index(name, data):
    names = find_player_match (name, data)

    if len(names) == 0:
        return f'{name} not found'

#    elif len(names) == 1:
    players_indexes = data[data['short_name'].isin(names)]
    return players_indexes['short_name']

#    elif len(names) <= 5:
#        print(f'Found {len(names)} players for your search')
#        for i, n in enumerate(names):
#            print(f'{i+1}.  {n}')
#        user_input = int(input('Please select the correct player number:  '))
#        try:
#            return data[data['short_name']== names[user_input -1]].index[0]
#        except:
#            print('Please retry, number  is not in the list')

#    else:
#        print(f'Found too many players for your search')
#        for i, n in enumerate(names[:5]):
#            print(f'{i+1}.  {n}')

#        user_input = int(input('Please select the correct player number:  '))
#        try:
#            return data[data['short_name']== names[user_input -1]].index[0]
#        except:
#            print('Please retry, number  is not in the list')
