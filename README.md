# How to config, build and run API and Docker image (Step by step)

## Create environment variables in .env file

- MODEL_TARGET=mlflow

- GCP_PROJECT=<your_gcp_project_id>
- GCP_REGION=europe-west1

- GOOGLE_APPLICATION_CREDENTIALS=credentials.json (here you need to copy the credentials.json to inside our project path. You can generate it running: gcloud auth application-default login)

- BQ_REGION=EU
- BQ_DATASET=APP
- BQ_TABLENAME=male_players_23
- BQ_TABLENAME_TSNE=tsne_data

- MLFLOW_TRACKING_URI=https://mlflow.lewagon.ai
- MLFLOW_EXPERIMENT=APP_experiment_<your_github_name>
- MLFLOW_MODEL_NAME=APP_<your_github_name>

- DOCKER_LOCAL_PORT=8080
- DOCKER_REPO_NAME=docker
- GAR_IMAGE=app

## Create Biq Query database and tables (run terminal)

bq mk \
    --project_id $GCP_PROJECT \
    --data_location $BQ_REGION \
    $BQ_DATASET

bq mk --location=$GCP_REGION $BQ_DATASET.$BQ_TABLENAME

bq mk --location=$GCP_REGION $BQ_DATASET.$BQ_TABLENAME_TSNE

## Populate tables for the first use (it takes +/- 11 minutes)

make create_bq_tables

## Fit model (it takes +/- 9 minutes)

make run_fit

## Run API (you can run and test to see if its all working before create Docker image)

make run_api

Control + C to stop the API when you are satisfied with your tests

## Create Docker image (run in the same path as Dockerfile and setup.py)

Launch docker app

docker info (to check if its running)

docker build --tag=$GAR_IMAGE:dev .  (it takes +/- 5 minutes)

docker images  (to see if the docker image is running. It needs to have a Repository called APP)

docker run -it -e PORT=8000 -p 8000:8000 $GAR_IMAGE:dev sh  (to check if you can go inside the docker image)

exit (to go out of the docker image)

docker run -e PORT=8000 -p 8000:8000 --env-file .env $GAR_IMAGE:dev  (to run the API from Docker Image)

Go to your browser and see if the API is running and working

## To stop Docker Image

docker ps  (get the Container ID)

docker container stop <Container_ID>
