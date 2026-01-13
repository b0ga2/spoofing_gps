import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn import svm
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
from pyod.models.auto_encoder import AutoEncoder

# Load Data
normal_df = pd.read_csv('feature_extraction.csv')
anomalous_df = pd.read_csv('feature_extraction_anomalous.csv')

normal_filled = normal_df.fillna(0)
anomalous_filled = anomalous_df.fillna(0)

# feature selection & transformation
all_cols = [c for c in normal_df.columns if c not in ['track_id', 'window_start_time', 'window_end_time']]
feature_cols = all_cols

print(f"Training on {len(feature_cols)} features: {feature_cols}")

# Identify Ground Truth
# We compare the two dataframes to find exactly which rows were modified
df1 = normal_filled[all_cols]
df2 = anomalous_filled[all_cols]
diff_mask = (df1 != df2).any(axis=1)

anomalous_indices = df1.index[diff_mask]
normal_indices = df1.index[~diff_mask]

print(f"Ground Truth: Found {len(anomalous_indices)} actual anomalies in the dataset.")

# Prepare Data & Apply Log Transform
# We use log1p to squash massive variance spikes (e.g. 100,000 -> 11.5)
# This makes the data "linearly separable" for models like Linear SVM.
X_train = np.log1p(np.abs(normal_filled[feature_cols].values))
X_test_anom = np.log1p(np.abs(anomalous_filled.loc[anomalous_indices, feature_cols].values))
X_test_norm = np.log1p(np.abs(anomalous_filled.loc[normal_indices, feature_cols].values))

# Scaling and PCA
scaler = RobustScaler()

# Dynamic PCA: Use 5 components, or fewer if we have fewer features
n_components = min(len(feature_cols), 5)
pca = PCA(n_components=n_components)

# Fit on training data
X_train_processed = pca.fit_transform(scaler.fit_transform(X_train))

# Transform test data
X_test_anom_processed = pca.transform(scaler.transform(X_test_anom))
X_test_norm_processed = pca.transform(scaler.transform(X_test_norm))

# Define the Models
outliers_fraction = 0.0001

anomaly_algorithms = [
    ("EllipticEnvelope", EllipticEnvelope(contamination=outliers_fraction, support_fraction=0.8, random_state=42)),
    ("One-Class SVM (Linear)", svm.OneClassSVM(nu=outliers_fraction, kernel="linear", gamma=0.1)),
    ("One-Class SVM (Poly)", svm.OneClassSVM(nu=outliers_fraction, kernel="poly", degree=5, gamma=0.1)),
    ("One-Class SVM (RBF)", svm.OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.1)),
    ("Isolation Forest", IsolationForest(contamination=outliers_fraction, random_state=42)),
    ("Local Outlier Factor", LocalOutlierFactor(n_neighbors=50, novelty=True, contamination=outliers_fraction)),
     ("Autoencoder", AutoEncoder(contamination=outliers_fraction, hidden_neuron_list=[16], verbose=0)),
]

print(f"\n--- Model Results ---")
print(f"Training on {len(X_train)} samples.")
print(f"Testing on {len(X_test_anom)} Anomalies and {len(X_test_norm)} Normal samples.\n")

for name, algorithm in anomaly_algorithms:
    # Train
    algorithm.fit(X_train_processed)

    # --- Prediction & Metrics Calculation ---
    if name == "Autoencoder":
        # PyOD: 1 = Anomaly (Positive), 0 = Normal (Negative)
        pred_anom = algorithm.predict(X_test_anom_processed)
        pred_norm = algorithm.predict(X_test_norm_processed)

        # True Positives: Anomalias previstas como 1
        TP = np.sum(pred_anom == 1)
        # False Negatives: Anomalias previstas como 0
        FN = np.sum(pred_anom == 0)

        # False Positives: Normais previstos como 1
        FP = np.sum(pred_norm == 1)
        # True Negatives: Normais previstos como 0
        TN = np.sum(pred_norm == 0)
    else:
        # Sklearn: -1 = Anomaly (Positive), 1 = Normal (Negative)
        pred_anom = algorithm.predict(X_test_anom_processed)
        pred_norm = algorithm.predict(X_test_norm_processed)

        # True Positives: Anomalias previstas como -1
        TP = np.sum(pred_anom == -1)
        # False Negatives: Anomalias previstas como 1
        FN = np.sum(pred_anom == 1)

        # False Positives: Normais previstos como -1
        FP = np.sum(pred_norm == -1)
        # True Negatives: Normais previstos como 1
        TN = np.sum(pred_norm == 1)

    # Recall (Sensitivity/TPR) = TP / (TP + FN)
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    # Precision = TP / (TP + FP)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0

    # F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"{name}:")
    print(f"  Confusion Matrix: [TP={TP}, TN={TN}, FP={FP}, FN={FN}]")
    print(f"  Recall (TPR):     {recall:.2%} ({TP}/{TP+FN})")
    print(f"  Precision:        {precision:.2%}")
    print(f"  F1-Score:         {f1_score:.4f}")
    print("-" * 30)

    cm = np.array([[TN, FP], [FN, TP]])
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Previsto Normal', 'Previsto Anómalo'],
                yticklabels=['Real Normal', 'Real Anómalo'])
    plt.title(f'Matriz de Confusão: {name}')
    plt.ylabel('Label Real')
    plt.xlabel('Label Prevista')
    plt.tight_layout()
    # plt.show()
