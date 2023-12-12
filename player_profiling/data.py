import pandas as pd
from pathlib import Path
from google.cloud import bigquery
from player_profiling.params import *
from player_profiling.preprocessor import filter_data, preprocess, preprocess_tsne
from player_profiling.data_enhancer import data_enhancer
import os
import json

def load_all_data():
    '''
    Function to return all players data
    '''

    root_path = os.path.dirname(os.path.dirname(__file__))
    filename = os.path.join(root_path, 'raw_data', 'male_players_23.csv')
    chunksize = 100000

    chunks = pd.read_csv(filename, chunksize=chunksize, iterator=True, low_memory=False)
    df = pd.concat(chunks, ignore_index=True)
#   df =pd.read_csv(filename, nrows= 10000) <- for quick calculations
    return df

def load_data_fifa23():
    '''
    Function to return the unique players from Fifa 23
    The most updated version of each player
    '''

    data = load_all_data()
    data_fifa23 = data[data['fifa_version'] == 23]

    data_fifa23 = data_fifa23.drop_duplicates('long_name')

    return data_fifa23


def get_data_with_cache(
        gcp_project:str,
        query:str,
        cache_path:Path,
        data_has_header=True
    ) -> pd.DataFrame:
    """
    Retrieve `query` data from BigQuery, or from `cache_path` if the file exists
    Store at `cache_path` if retrieved from BigQuery for future use
    """

    if cache_path.is_file():
        print("\nLoad data from local CSV...")
        df = pd.read_csv(cache_path, header='infer' if data_has_header else None)
    else:
        print("\nLoad data from BigQuery server...")
        client = bigquery.Client(project=gcp_project)
        query_job = client.query(query)
        result = query_job.result()
        df = result.to_dataframe()

        # Store as CSV if the BQ query returned at least one valid line
        if df.shape[0] > 1:
            df.to_csv(cache_path, header=data_has_header, index=False)

    print(f"✅ Data loaded, with shape {df.shape}")

    return df

def load_data_to_bq(
        data: pd.DataFrame,
        gcp_project:str,
        bq_dataset:str,
        table: str,
        truncate: bool
    ):
    """
    - Save the DataFrame to BigQuery
    - Empty the table beforehand if `truncate` is True, append otherwise
    """

    assert isinstance(data, pd.DataFrame)
    full_table_name = f"{gcp_project}.{bq_dataset}.{table}"
    print(f"\nSave data to BigQuery @ {full_table_name}...:")

    if table == BQ_TABLENAME_TSNE:
        data.columns = [f"_{column}" if not str(column)[0].isalpha() and not str(column)[0] == "_" else str(column) for column in data.columns]

    client = bigquery.Client(project=gcp_project)

    # Define write mode and schema
    write_mode = "WRITE_TRUNCATE" if truncate else "WRITE_APPEND"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    print(f"\n{'Write' if truncate else 'Append'} {full_table_name} ({data.shape[0]} rows)")

    # Load data
    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    result = job.result()  # wait for the job to complete

    print(f"✅ Data saved to bigquery, with shape {data.shape}")

def create_bq_tables():
    '''
    Function to create Big Query Database
    '''

    print(f"\nLoading data and creating bigquery table...:")
    data = load_data_fifa23()

    # Create label column
    data['label'] = 0
    data['idx'] = data.index

    root_path = os.path.dirname(os.path.dirname(__file__))
    filename = os.path.join(root_path, 'raw_data', 'continent.json')

    data = data_enhancer(data, filename)

    load_data_to_bq(
        data,
        gcp_project=GCP_PROJECT,
        bq_dataset=BQ_DATASET,
        table=BQ_TABLENAME,
        truncate=True
    )
    print(f"\n✅ Data and table ready")

    print(f"\nPreprocessing data and creating bigquery tsne table...:")
    data_filtered = filter_data(data)
    data_preproc = preprocess(data_filtered)
    data_preproc_tsne = pd.DataFrame(preprocess_tsne(data_preproc))

    data_preproc_tsne['idx'] = data_preproc_tsne.index

    load_data_to_bq(
        data_preproc_tsne,
        gcp_project=GCP_PROJECT,
        bq_dataset=BQ_DATASET,
        table=BQ_TABLENAME_TSNE,
        truncate=True
    )
    print(f"\n✅ All Done")

if __name__ == '__main__':
    print(load_all_data().head())
