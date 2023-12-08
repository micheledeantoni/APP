#      Standard version
FROM python:3.10.6-buster

# Copy everything we need into the image
COPY player_profiling player_profiling
COPY api api
COPY scripts scripts
COPY requirements.txt requirements_docker.txt
COPY setup.py setup.py
COPY credentials.json credentials.json
COPY Makefile Makefile

# Install everything
RUN pip install --upgrade pip
RUN pip install -r requirements_docker.txt
RUN pip install .

# Make directories that we need, but that are not included in the COPY
RUN mkdir /raw_data
RUN mkdir /models
RUN make reset_local_files

CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
