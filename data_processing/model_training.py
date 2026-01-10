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
    normalDataFile=sys.argv[1]
    anomalyDataFile=sys.argv[2]

    normalData=load_and_clean_data(normalDataFile)
    anomalyData=load_and_clean_data(anomalyDataFile)
    nallN,cN=normalData.shape
    nA,cA=anomalyData.shape

    percTrain=0.5
    train=normalData[:int(percTrain*nallN)]
    test=np.concatenate([normalData[int(percTrain*nallN):],anomalyData],axis=0)

    nN=int((1-percTrain)*nallN)
    print(train.shape)

    outliers_fraction = 0.0001

    anomaly_algorithms = [
        ("EllipticEnvelope", EllipticEnvelope(contamination=outliers_fraction, support_fraction=0.8, random_state=42)),
        ("One-Class SVM (Linear)", svm.OneClassSVM(nu=outliers_fraction, kernel="linear", gamma=0.1)),
        ("One-Class SVM (Poly)", svm.OneClassSVM(nu=outliers_fraction, kernel="poly",degree=5, gamma=0.1)),
        ("One-Class SVM (RBF)", svm.OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.1)),
        ("Isolation Forest",IsolationForest(contamination=outliers_fraction, random_state=42),),
        ("Local Outlier Factor",LocalOutlierFactor(n_neighbors=50, novelty=True, contamination=outliers_fraction),),
        ("Autoencoder",AutoEncoder(contamination=outliers_fraction,hidden_neuron_list=[16]),),
    ]

    rng = np.random.seed(42)

    scaler = MaxAbsScaler()
    #scaler = StandardScaler()
    scaler.fit(train)
    trainScaled=scaler.transform(train)
    testScaled=scaler.transform(test)

    #from sklearn.decomposition import PCA
    #pca = PCA(n_components=8)
    #pca.fit(trainScaled)
    #trainScaled=pca.transform(trainScaled)
    #testScaled=pca.transform(testScaled)

    for name, algorithm in anomaly_algorithms:
        alg = algorithm
        alg.fit(trainScaled)

        Apred=alg.predict(testScaled)

        if name=="Autoencoder":
            Apred=-2*Apred+1

        TN=100*sum(Apred[:nN]==1)/nN
        FP=100*sum(Apred[:nN]==-1)/nN
        FN=100*sum(Apred[nN:]==1)/nA
        TP=100*sum(Apred[nN:]==-1)/nA

        print(f"{name}: False positives {FP:.2f}%, Anomalies detected {TP:.2f}%")
