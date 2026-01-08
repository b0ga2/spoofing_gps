#!/usr/bin/env bash

set -xe

python data_cleaning.py
python generate_features.py
python feature_extraction.py
python model_training.py
