import pandas as pd
from data_cleaning import load_csv 
from datetime import datetime, timedelta
import math
import csv

def get_features_stats(windata,cols):
  features=[]
  
  features = features+list(windata[cols].mean())
  features = features+list(windata[cols].var())
  features = features+list(windata[cols].max())
  features = features+list(windata[cols].min())
  features = features+list(windata[cols].quantile(0.9))

  return(features)


def grouping_by_time(size_window: int, sliding_time: int) -> pd.DataFrame:
    data = load_csv("dados_gps_analisados.csv")
    data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d %H:%M:%S")

    cols_stats = ["speed_mps", "speed_kmh", "acceleration_mps2", "acceleration_kmh2", "bearing_deg"]
    
    # 1. FIX: Update this list to match exactly what get_features_stats returns
    # Your function does: mean, var, max, min, quantile(0.9)
    calculated_stats = ["mean", "var", "max", "min", "quantile_0.9"]

    # 2. FIX: Swap the loop order
    # Because get_features_stats adds ALL means first, then ALL vars, etc.
    # we must iterate 'stat' first, then 'col'.
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
                
                # Verify length matching (Optional debug print)
                # if len(features_values) != len(feature_headers):
                #     print(f"Mismatch! Data: {len(features_values)}, Headers: {len(feature_headers)}")
                
                row_data = [track_id, current_start, current_end] + features_values
                all_window_results.append(row_data)

            current_start += step_duration

    result_df = pd.DataFrame(all_window_results, columns=final_headers)
    result_df.to_csv("windowed_features.csv", index=False)

    return result_df


grouping_by_time(30, 15)