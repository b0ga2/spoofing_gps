#!/usr/bin/env bash

set -xe

python generate_anomalous.py go_track_trackspoints.csv go_track_trackspoints_anomalous.csv

python data_cleaning.py go_track_trackspoints.csv data_cleaning.csv
python data_cleaning.py go_track_trackspoints_anomalous.csv data_cleaning_anomalous.csv

python generate_features.py data_cleaning.csv generate_features.csv
python generate_features.py data_cleaning_anomalous.csv generate_features_anomalous.csv

python feature_extraction.py generate_features.csv feature_extraction.csv
python feature_extraction.py generate_features_anomalous.csv feature_extraction_anomalous.csv

python model_training.py feature_extraction.csv feature_extraction_anomalous.csv
