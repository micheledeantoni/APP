from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from player_profiling.data import get_data_with_cache
from player_profiling.utils import find_closest_players, find_player_index
from player_profiling.params import *
from player_profiling.registry import load_model
from pathlib import Path

app = FastAPI()

print("\nLoading data...")
query = f"""
        SELECT *
        FROM {GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLENAME}
        ORDER BY idx
    """

data_cache_path = Path(LOCAL_DATA_PATH).joinpath(f"{BQ_TABLENAME}.csv")

app.state.data = get_data_with_cache(gcp_project=GCP_PROJECT,
                                     query=query,
                                     cache_path=data_cache_path,
                                     data_has_header=True
)
print("✅ data loaded \n")

print("\nLoading tsne...")
query = f"""
        SELECT *
        FROM {GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLENAME_TSNE}
        ORDER BY idx
    """
tsne_cache_path = Path(LOCAL_DATA_PATH).joinpath(f"{BQ_TABLENAME_TSNE}.csv")
app.state.tsne = get_data_with_cache(gcp_project=GCP_PROJECT,
                                     query=query,
                                     cache_path=tsne_cache_path,
                                     data_has_header=True
)
print("✅ tsne loaded \n")

print("\nLoading model...")
app.state.model = load_model()
print("✅ model loaded \n")

print("")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return {
        'message': "API is running!"
    }

@app.get("/players-suggestion")
def get_players_suggestion(player_index = int, continent = None, experience = None,
                           wage_range = None, value_range= None, league_level = None):
    '''
    Endpoint to return suggested players
    '''

    closest_players = find_closest_players(player_index, app.state.data, app.state.tsne,
                                           continent, experience, wage_range, value_range, league_level)
    closest_players = closest_players.to_dict(orient="records")

    return {
        'players': closest_players,
    }

@app.get("/find_player_by_name")
def get_find_player_by_name(player_name: str):
    '''
    Endpoint to return players by name
    '''

    players_indexes = find_player_index(player_name, app.state.data)
    players_indexes = players_indexes.to_dict(orient="records")

    return {
        'players': players_indexes,
    }
