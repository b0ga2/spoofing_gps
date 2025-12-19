import sys
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MaxAbsScaler

# Try importing PyOD
try:
    from pyod.models.auto_encoder import AutoEncoder
except ImportError:
    AutoEncoder = None

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    
    # 1. Remove Metadata
    cols_to_drop = ['track_id', 'window_start_time', 'window_end_time']
    existing_meta = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=existing_meta)
    
    # 2. Remove Redundant Columns (Fix for "Singular Matrix" error)
    # We drop 'kmh' columns because they are perfect duplicates of 'mps' columns * 3.6
    # Also drop 'kmh2' for acceleration.
    cols_redundant = [c for c in df.columns if 'kmh' in c]
    if cols_redundant:
        print(f"Removing redundant columns to prevent matrix errors: {cols_redundant}")
        df = df.drop(columns=cols_redundant)
        
    # 3. Handle NaNs
    df = df.fillna(0)
    
    return df.values

# --- Main Script ---

if len(sys.argv) >= 3:
    normalDataFile = sys.argv[1]
    anomalyDataFile = sys.argv[2]
else:
    normalDataFile = "windowed_features.csv"
    anomalyDataFile = "windowed_features.csv" # Change this if you have a separate anomaly file

print("Loading and cleaning data...")
normalData = load_and_clean_data(normalDataFile)

# Load anomaly data
if normalDataFile != anomalyDataFile:
    anomalyData = load_and_clean_data(anomalyDataFile)
else:
    # If using the same file, we assume no anomalies for this test run
    # OR you can simulate some if needed.
    anomalyData = np.array([]) 

nallN = normalData.shape[0]

# Train/Test Split
percTrain = 0.5
n_train = int(percTrain * nallN)

train = normalData[:n_train]

if anomalyData.size > 0:
    test = np.concatenate([normalData[n_train:], anomalyData], axis=0)
    nA = anomalyData.shape[0]
else:
    test = normalData[n_train:]
    nA = 0

print(f"Training shape: {train.shape}")
print(f"Test shape: {test.shape}")

# Scale Data
scaler = MaxAbsScaler()
scaler.fit(train)
trainScaled = scaler.transform(train)
testScaled = scaler.transform(test)

outliers_fraction = 0.0001

anomaly_algorithms = [
    ("EllipticEnvelope", EllipticEnvelope(contamination=outliers_fraction, support_fraction=0.9, random_state=42)),
    ("One-Class SVM (Linear)", svm.OneClassSVM(nu=outliers_fraction, kernel="linear", gamma=0.1)),
    ("One-Class SVM (RBF)", svm.OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.1)),
    ("Isolation Forest", IsolationForest(contamination=outliers_fraction, random_state=42)),
    ("Local Outlier Factor", LocalOutlierFactor(n_neighbors=20, novelty=True, contamination=outliers_fraction)),
]

if AutoEncoder:
    anomaly_algorithms.append(
        ("Autoencoder", AutoEncoder(contamination=outliers_fraction, hidden_neuron_list=[8, 4, 8], epochs=30))
    )

nN = int((1 - percTrain) * nallN) 

print("\n--- Improved Results ---")
for name, algorithm in anomaly_algorithms:
    alg = algorithm
    
    try:
        alg.fit(trainScaled)
        Apred = alg.predict(testScaled)
    except Exception as e:
        print(f"{name}: Failed - {e}")
        continue
    
    # Fix AutoEncoder output to match Sklearn (1=Inlier, -1=Outlier)
    if name == "Autoencoder":
        Apred = np.where(Apred == 0, 1, -1)

    # Metrics
    TN_count = sum(Apred[:nN] == 1)
    FP_count = sum(Apred[:nN] == -1)
    
    FP_perc = 100 * FP_count / nN
    
    if nA > 0:
        TP_count = sum(Apred[nN:] == -1)
        TP_perc = 100 * TP_count / nA
        print(f"{name}: FP (False Alarms) {FP_perc:.2f}% | TP (Detection) {TP_perc:.2f}%")
    else:
        print(f"{name}: FP (False Alarms) {FP_perc:.2f}% | TP (Detection) N/A (No Anomalies)")