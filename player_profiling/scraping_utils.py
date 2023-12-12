import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to standardize season format
def standardize_season_format(season):
    """Converts season formats to a standard 'YY/YY' format."""
    if '/' not in season:
        start_year = int(season) - 1
        return f"{str(start_year)[-2:]}/{season[-2:]}"
    return season

# Function to create search URL
def create_search_url(player_name):
    base_search_url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query="
    formatted_name = player_name.replace(" ", "+")
    return base_search_url + formatted_name

# Function to scrape player data
def get_player_data(search_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        player_data = []

        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        player_url = soup.find("td", class_="hauptlink").find("a")['href']
        player_url = player_url.replace("profil", "leistungsdatendetails")
        player_url = player_url + '/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1'
        details_player_url = 'https://www.transfermarkt.com' + player_url

        response = requests.get(details_player_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        position_element = soup.find_all("span", class_="data-header__content")[7]
        position = position_element.get_text(strip=True) if position_element else "Unknown"

        for row in soup.find("table", class_="items").find("tbody").find_all("tr", class_=["odd", "even"]):
            columns = row.find_all("td")
            season = columns[0].get_text(strip=True)
            season = standardize_season_format(season)  # Standardize season format here
            competition_link = columns[2].find("a", title=True)
            competition = competition_link['title'] if competition_link else "Unknown"

            if position == 'Goalkeeper':
                appearances = int(columns[5].get_text(strip=True).replace("-", "0"))
                pps = float(columns[6].get_text(strip=True).replace("-", "0").replace(",", "."))
                goals_conceded = int(columns[14].get_text(strip=True).replace("-", "0"))
                clean_sheets = int(columns[15].get_text(strip=True).replace("-", "0"))
                minutes_played = columns[16].get_text(strip=True).replace('-', '0').replace('.', '').replace('\'', '')
                minutes_played = int(minutes_played) if minutes_played.isdigit() else 0
                player_data.append({
                    'season': season,
                    'competition': competition,
                    'appearances': appearances,
                    'PPS': pps,
                    'goals_conceded': goals_conceded,
                    'clean_sheets': clean_sheets,
                    'minutes_played': minutes_played
                })
            else:
                appearances = int(columns[5].get_text(strip=True).replace("-", "0"))
                pps = float(columns[6].get_text(strip=True).replace("-", "0").replace(",", "."))
                goals = int(columns[7].get_text(strip=True).replace("-", "0"))
                assists = int(columns[8].get_text(strip=True).replace("-", "0"))
                minutes_played = columns[17].get_text(strip=True).replace('-', '0').replace('.', '').replace('\'', '')
                minutes_played = int(minutes_played) if minutes_played.isdigit() else 0
                player_data.append({
                    'season': season,
                    'competition': competition,
                    'appearances': appearances,
                    'PPS': pps,
                    'goals': goals,
                    'assists': assists,
                    'minutes_played': minutes_played
                })

        return pd.DataFrame(player_data)


    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def add_trendline(ax, data, color):
    # Define the range of seasons for the trend line
    seasons_range = ['18/19', '19/20', '20/21', '21/22', '22/23']

    # Filter data to include only the defined range
    filtered_data = data.loc[data.index.intersection(seasons_range)]

    # Calculate and plot the trend line if there is any data
    if not filtered_data.empty:
        z = np.polyfit(np.arange(len(filtered_data)), filtered_data, 1)
        p = np.poly1d(z)
        ax.plot(filtered_data.index, p(np.arange(len(filtered_data))), color=color, linestyle='--')
        slope = round(z[0], 2)
        ax.text(0.05, 0.95, f'Trend: {slope}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color=color)

def plot_metrics(player_name):
    # Player selection
    search_url = create_search_url(player_name)
    scraped_df = get_player_data(search_url)

    try:
        # Filter the DataFrame to only include rows where 'minutes_played' >= 45
        scraped_df = scraped_df[scraped_df['minutes_played'] >= 45]
        scraped_df = scraped_df[scraped_df['PPS'] != 0]

        # Focus only on the most recent 5 seasons
        recent_seasons = sorted(scraped_df['season'].unique(), reverse=True)[:5]
        scraped_df = scraped_df[scraped_df['season'].isin(recent_seasons)]

        # Show DataFrame
        #print(scraped_df)

        # Check if the player is a goalkeeper
        is_goalkeeper = 'goals_conceded' in scraped_df.columns

        # Aggregate data by season
        if is_goalkeeper:
            aggregated_data = scraped_df.groupby('season').agg({
                'PPS': 'mean',
                'goals_conceded': 'sum',
                'clean_sheets': 'sum',
                'minutes_played': 'sum',
                'appearances': 'sum'
            }).sort_index()

            # Calculate additional metrics
            aggregated_data['average_goals_conceded_per_appearance'] = aggregated_data['goals_conceded'] / aggregated_data['appearances']
            aggregated_data['clean_sheet_per_appearance'] = aggregated_data['clean_sheets'] / aggregated_data['appearances']

            metrics = ['appearances', 'PPS', 'average_goals_conceded_per_appearance', 'clean_sheet_per_appearance', 'minutes_played']
        else:
            aggregated_data = scraped_df.groupby('season').agg({
                'appearances': 'sum',
                'PPS': 'mean',
                'goals': 'sum',
                'assists': 'sum',
                'minutes_played': 'sum'
            }).sort_index()
            metrics = ['appearances', 'PPS', 'goals', 'assists', 'minutes_played']

        # Visualization
        colors = ['#1f77b4', '#7f7f7f', '#aec7e8', '#c7c7c7']  # Shades of blue and grey
        fig, axes = plt.subplots(nrows=1, ncols=len(metrics), figsize=(20, 5))


        # Plot each metric
        for i, metric in enumerate(metrics):
            aggregated_data[metric].plot(kind='bar', color=colors[i % len(colors)], ax=axes[i])
            add_trendline(axes[i], aggregated_data[metric], color='black')
            axes[i].set_title(f'{metric.replace("_", " ").capitalize()} per season')
            axes[i].set_ylabel(metric.replace("_", " ").capitalize())

        plt.tight_layout()
        plt.show()
    except:
        return 'Data is not available for the selected player'

def from_index_to_name(data, index):
    return ' '.join(data['player_url'][index].split('/')[-2].split('-'))
