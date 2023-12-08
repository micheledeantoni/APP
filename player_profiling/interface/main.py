from pathlib import Path
import pandas as pd

from player_profiling.params import *
from player_profiling.preprocessor import filter_data, preprocess, preprocess_tsne
from player_profiling.registry import load_model, save_model, mlflow_transition_model, mlflow_run
from player_profiling.model import initialize_model_kmeans, initialize_model_spectral, fit_model
from player_profiling.data import get_data_with_cache, load_data_to_bq

@mlflow_run
def fit(model_type = 'kmeans'):
    """
    - Download data from BQ table (or from cache if it exists)
    - Preprocess data
    - Fit model
    """

    print("\n⭐️ Use case: fit")
    print("\nLoading data...")

    query = f"""
        SELECT *
        FROM {GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLENAME}
        ORDER BY idx
    """

    data_cache_path = Path(LOCAL_DATA_PATH).joinpath(f"{BQ_TABLENAME}.csv")
    data = get_data_with_cache(
        gcp_project=GCP_PROJECT,
        query=query,
        cache_path=data_cache_path,
        data_has_header=True
    )

    data = data.drop(columns=['idx'])
    if data.shape[0] < 10:
        print("❌ Not enough processed data retrieved to fit")
        return None

    print("\nFiltering features...")
    data_filtered = filter_data(data)
    print("\nPreprocessing data...")
    data_preproc = preprocess(data_filtered)
    print("\nPreprocessing data tsne...")
    data_preproc_tsne = pd.DataFrame(preprocess_tsne(data_preproc))

    data_preproc_tsne['idx'] = data_preproc_tsne.index

    load_data_to_bq(data_preproc_tsne,
        gcp_project=GCP_PROJECT,
        bq_dataset=BQ_DATASET,
        table=BQ_TABLENAME_TSNE,
        truncate=True)

    print("\nLoading model...")
    model = load_model()

    if model is None:
        if model_type == 'kmeans':
            model = initialize_model_kmeans()
        else:
            model = initialize_model_spectral()

    print("\nFitting model...")
    model = fit_model(model, data_preproc_tsne)

    save_model(model=model)

    if MODEL_TARGET == 'mlflow':
        mlflow_transition_model(current_stage="None", new_stage="Production")

    # Create label column on data and save
    data['label'] = model.labels_
    data['idx'] = data.index

    load_data_to_bq(data,
        gcp_project=GCP_PROJECT,
        bq_dataset=BQ_DATASET,
        table=BQ_TABLENAME,
        truncate=True)

    print("✅ fit() done \n")


if __name__ == '__main__':
    fit(model_type = 'kmeans')
