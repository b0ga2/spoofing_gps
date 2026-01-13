from data_cleaning import load_csv # Assuming this exists as per your original file
from datetime import timedelta
import pandas as pd
import numpy as np
import sys

def get_features_stats(windata, cols):
    features = []
    
    # Calculate base stats
    means = windata[cols].mean()
    variances = windata[cols].var().fillna(0)
    maxs = windata[cols].max()
    mins = windata[cols].min()
    quantiles = windata[cols].quantile(0.9)

    # 1. Mean
    features = features + list(means)
    # 2. Variance
    features = features + list(variances)
    # 3. Max
    features = features + list(maxs)
    # 4. Min
    features = features + list(mins)
    # 5. Quantile
    features = features + list(quantiles)
    
    # 6. NEW STATISTIC: Log Variance
    # We use log1p (log(1+x)) to handle zeros safely and squash massive spikes
    log_variances = np.log1p(variances)
    features = features + list(log_variances)

    return features

def grouping_by_time(size_window: int, sliding_time: int):
    data = load_csv(sys.argv[1])
    data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d %H:%M:%S")

    # Added "jerk_mps3" to the columns list
    cols_stats = ["speed_mps", "acceleration_mps2", "jerk_mps3", "bearing_deg"]
    
    # Added "log_var" to the stats list
    calculated_stats = ["mean", "var", "max", "min", "quantile_0.9", "log_var"]

    # Generate headers dynamically
    feature_headers = [f"{col}_{stat}" for stat in calculated_stats for col in cols_stats]
    final_headers = ["track_id", "window_start_time", "window_end_time"] + feature_headers

    list_track_id = data['track_id'].unique().tolist()
    all_window_results = []

    for track_id in list_track_id:
        df = data[data['track_id'] == track_id].sort_values('time')
        if df.empty:
            continue

        Tstart = df.iloc[0]["time"]
        Tend = df.iloc[-1]["time"]

        window_duration = timedelta(seconds=size_window)
        step_duration = timedelta(seconds=sliding_time)

        current_start = Tstart
        while current_start + window_duration <= Tend:
            current_end = current_start + window_duration
            windata = df[(df["time"] >= current_start) & (df["time"] < current_end)]

            if not windata.empty:
                features_values = get_features_stats(windata, cols_stats)
                row_data = [track_id, current_start, current_end] + features_values
                all_window_results.append(row_data)

            current_start += step_duration

    result_df = pd.DataFrame(all_window_results, columns=final_headers)
    result_df.to_csv(sys.argv[2], index=False)
    print(f"Extraction complete. New features (Log-Var & Jerk) saved to {sys.argv[2]}")

    return result_df

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python feature_extraction.py <input_csv> <output_csv>")
    else:
        grouping_by_time(30, 15)