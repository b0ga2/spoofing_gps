import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn import svm
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
from pyod.models.auto_encoder import AutoEncoder
import warnings

warnings.filterwarnings("ignore")

normal_df = pd.read_csv('feature_extraction.csv')
anomalous_df = pd.read_csv('feature_extraction_anomalous.csv')

normal_filled = normal_df.fillna(0)
anomalous_filled = anomalous_df.fillna(0)

all_cols = [c for c in normal_df.columns if c not in ['track_id', 'window_start_time', 'window_end_time']]
feature_cols = all_cols

print(f"Features selecionadas: {len(feature_cols)}")

outliers_fraction = 0.01
model_templates = [
    ("EllipticEnvelope", lambda: EllipticEnvelope(contamination=outliers_fraction, support_fraction=0.8, random_state=42)),
    ("One-Class SVM (Linear)", lambda: svm.OneClassSVM(nu=outliers_fraction, kernel="linear", gamma=0.1)),
    ("One-Class SVM (Poly)", lambda: svm.OneClassSVM(nu=outliers_fraction, kernel="poly", degree=5, gamma=0.1, max_iter=5000)),
    ("One-Class SVM (RBF)", lambda: svm.OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.1)),
    ("Isolation Forest", lambda: IsolationForest(contamination=outliers_fraction, random_state=42)),
    ("Local Outlier Factor", lambda: LocalOutlierFactor(n_neighbors=50, novelty=True, contamination=outliers_fraction)),
     ("Autoencoder", lambda: AutoEncoder(contamination=outliers_fraction, hidden_neuron_list=[16], verbose=0)),
]

# Lista para guardar os resultados para exportação CSV posterior
detailed_results = []

unique_tracks = normal_filled['track_id'].unique()
print(f"A processar {len(unique_tracks)} tracks individualmente...\n")

for track_id in unique_tracks:
    track_normal = normal_filled[normal_filled['track_id'] == track_id]
    track_anomalous = anomalous_filled[anomalous_filled['track_id'] == track_id]

    if len(track_normal) < 5: 
        continue

    # Identificar Ground Truth
    df1_local = track_normal[all_cols].reset_index(drop=True)
    df2_local = track_anomalous[all_cols].reset_index(drop=True)

    diff_mask = (df1_local != df2_local).any(axis=1)

    anom_idx_local = df1_local.index[diff_mask]
    norm_idx_local = df1_local.index[~diff_mask]

    # Contagem de anomalias reais neste track
    total_real_anomalies = len(anom_idx_local)
    total_lines = len(norm_idx_local)

    X_raw_train = track_normal[feature_cols].values
    X_raw_test_anom = track_anomalous.iloc[anom_idx_local][feature_cols].values
    X_raw_test_norm = track_anomalous.iloc[norm_idx_local][feature_cols].values

    X_train = np.log1p(np.abs(X_raw_train))
    X_test_anom = np.log1p(np.abs(X_raw_test_anom)) if len(X_raw_test_anom) > 0 else np.empty((0, len(feature_cols)))
    X_test_norm = np.log1p(np.abs(X_raw_test_norm))

    scaler = RobustScaler()
    n_comp = min(len(feature_cols), len(X_train), 5)

    if n_comp < 1: 
        n_comp = 1

    pca = PCA(n_components=n_comp)

    try:
        X_train_proc = pca.fit_transform(scaler.fit_transform(X_train))
        X_test_anom_proc = pca.transform(scaler.transform(X_test_anom)) if len(X_test_anom) > 0 else np.empty((0, n_comp))
        X_test_norm_proc = pca.transform(scaler.transform(X_test_norm)) if len(X_test_norm) > 0 else np.empty((0, n_comp))
    except Exception:
        continue

    print(f"\n>>> TRACK ID: {track_id} (Anomalias Reais: {total_real_anomalies}) (Total de linhas normais: {total_lines}) (Total de linhas: {len(df1_local)})")
    print("-" * 60)

    # Treinar e Testar
    for name, model_factory in model_templates:
        try:
            algorithm = model_factory()
            algorithm.fit(X_train_proc)

            # Prediction Logic
            if name == "Autoencoder":
                pred_anom = algorithm.predict(X_test_anom_proc) if len(X_test_anom_proc) > 0 else []
                pred_norm = algorithm.predict(X_test_norm_proc) if len(X_test_norm_proc) > 0 else []
                tp = np.sum(pred_anom == 1)
                fn = np.sum(pred_anom == 0)
                fp = np.sum(pred_norm == 1)
                tn = np.sum(pred_norm == 0)
            else:
                pred_anom = algorithm.predict(X_test_anom_proc) if len(X_test_anom_proc) > 0 else []
                pred_norm = algorithm.predict(X_test_norm_proc) if len(X_test_norm_proc) > 0 else []
                tp = np.sum(pred_anom == -1)
                fn = np.sum(pred_anom == 1)
                fp = np.sum(pred_norm == -1)
                tn = np.sum(pred_norm == 1)

            # Metrics Calculation
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            print(f"Modelo: {name:<25} | F1: {f1_score:.4f} | Recall: {recall:.2%} | Precision: {precision:.2%} | [TP={tp}, FP={fp}]")

            detailed_results.append({
                "Track_ID": track_id,
                "Model": name,
                "Real_Anomalies": total_real_anomalies,
                "TP": tp,
                "TN": tn,
                "FP": fp,
                "FN": fn,
                "Recall": recall,
                "Precision": precision,
                "F1_Score": f1_score
            })

        except Exception as e:
            print(f"Erro no modelo {name}: {e}")

if detailed_results:
    results_df = pd.DataFrame(detailed_results)
    output_filename = "resultados_detalhados_por_track.csv"
    results_df.to_csv(output_filename, index=False)
    print(f"\n\n[Concluído] Resultados detalhados guardados em: {output_filename}")
    
    print("\nTop 5 Melhores Deteções (F1-Score):")
    print(results_df.sort_values(by="F1_Score", ascending=False).head(5)[['Track_ID', 'Model', 'F1_Score', 'TP', 'FP']])
else:
    print("Nenhum resultado gerado.")
