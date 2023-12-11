import pandas as pd
import requests
import json


def find_continent(country):
    url = 'https://restcountries.com/v3.1/name/'
    response = requests.get(url + country)
    #time.sleep(2)
    if response.status_code == 200:
        return response.json()[0]['region']
    else:
        return 'Other'

def continent_dictionary(data):
    '''
    Creates a dictionary of nations:continent
    '''
    cont_dict = {}
    count = 0
    for c in data['nationality_name'].unique():
        count += 1
        print(f"iteration {count} / {len(data['nationality_name'].unique())}")
        cont_dict[c]=find_continent(c)
    return cont_dict

def player_experience (age):
    if age <= 20:
        return 'Prospect'
    elif age > 20 and age <= 25:
        return 'Emerging Talent'
    elif age > 25 and age <= 30:
        return 'Established Player'
    elif age > 30 and age <= 35:
        return 'Peak Performance'
    else:
        return 'Experienced Campaigner'

def league_level_bin(league_level):
    return '1st' if league_level == 1 else '2nd'

def wage_range_calc(wage):
    if wage > 25000:
        return 'High salary'
    elif wage > 16000 and wage <= 25000:
        return 'Medium-high salary'
    elif wage > 7000 and wage <= 16000:
        return 'Medium-low salary'
    else:
        return 'Low salary'


def value_range_calc(value):
    if value > 100_000_000:
        return 'Crazily expensive'
    elif value > 50_000_000 and value <= 100_000_000:
        return 'Really expensive'
    elif value > 25_000_000 and value <= 50_000_000:
        return 'Expensive'
    elif value > 7_000_000 and value <= 25_000_000:
        return 'Affordable'
    else:
        return 'Good deal'

def data_enhancer(data, cont_json = None):
    '''
    It adds some useful columns for filtering
    '''
    if cont_json:
        with open(cont_json, 'r') as file:
            cont_dict = json.load(file)
        data['Continent']= data['nationality_name'].map(cont_dict)
    else:
        data['Continent']= data['nationality_name'].map(continent_dictionary(data))
    data['wage_range']= data['wage_eur'].apply(wage_range_calc)
    data['experience']= data['age'].apply(player_experience)
    data['wage_range']= data['wage_eur'].apply(wage_range_calc)
    data['value_range'] = data['value_eur'].apply(value_range_calc)
    data['league_level_bin'] = data['league_level'].apply(league_level_bin)

    return data
