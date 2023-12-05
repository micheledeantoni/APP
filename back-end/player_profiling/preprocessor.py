import pandas as pd

def load_data_fifa23():
    '''
    Function to return the unique players from Fifa 23
    The most updated version of each player
    '''

    data = pd.read_csv('../raw_data/male_players_23.csv')
    #data = pd.read_csv('/Users/michele/code/micheledeantoni/APP/back-end/raw_data/male_players_23.csv')

    data_fifa23 = data[data['fifa_version'] == 23]

    data_fifa23 = data_fifa23.drop_duplicates('long_name')

    return data_fifa23
