from sklearn.neighbors import LocalOutlierFactor
from pyod.models.auto_encoder import AutoEncoder
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import MaxAbsScaler
from sklearn.ensemble import IsolationForest
from data_cleaning import load_csv
from sklearn import svm
import numpy as np, sys

def load_and_clean_data(filepath):
    df = load_csv(filepath)

    # remove metadata
    cols_to_drop = ['track_id', 'window_start_time', 'window_end_time']
    existing_meta = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=existing_meta)

    # handle NaNs
    df = df.fillna(0)
    return df.values

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        normalDataFile = sys.argv[1]
        anomalyDataFile = sys.argv[2]
    else:
        normalDataFile = "feature_extraction.csv"
        anomalyDataFile = "windowed_anomaly_features.csv"

    print("Loading and cleaning normal data...")
    normalData = load_and_clean_data(normalDataFile)

    # load anomaly data
    if normalDataFile != anomalyDataFile:
        print("Loading and cleaning anomaly data...")
        anomalyData = load_and_clean_data(anomalyDataFile)
    else:
        # if using the same file, we assume no anomalies for this test run or you can simulate some if needed.
        anomalyData = np.array([]) 

    nallN = normalData.shape[0]

    # train/test split
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

    # scale data
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
            ("Autoencoder", AutoEncoder(contamination=outliers_fraction, hidden_neuron_list=[8, 4, 8], epoch_num=30))
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
        
        # fix autoencoder output to match sklearn (1=inlier, -1=outlier)
        if name == "Autoencoder":
            Apred = np.where(Apred == 0, 1, -1)

        # metrics
        TN_count = sum(Apred[:nN] == 1)
        FP_count = sum(Apred[:nN] == -1)
        
        FP_perc = 100 * FP_count / nN
        
        if nA > 0:
            TP_count = sum(Apred[nN:] == -1)
            TP_perc = 100 * TP_count / nA
            print(f"{name}: FP (False Alarms) {FP_perc:.2f}% | TP (Detection) {TP_perc:.2f}%")
        else:
            print(f"{name}: FP (False Alarms) {FP_perc:.2f}% | TP (Detection) N/A (No Anomalies)")
