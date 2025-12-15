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

def grouping_by_time(seconds: int) -> pd.DataFrame:

    data = load_csv("dados_gps_analisados.csv")

    slide = seconds

    data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d %H:%M:%S")

    # Columns to extract the features   
    cols_stats=["speed_mps","speed_kmh","acceleration_mps2","acceleration_kmh2","bearing_deg"]

    # Separate by track id
    df1 = data.groupby(['track_id']).count()
    list_track_id = df1['id'].keys().to_list()

    print(list_track_id)
    
    header = (
      ["window_id"] + 
      [f"{col}_mean" for col in cols_stats] +
      [f"{col}_var" for col in cols_stats] +
      [f"{col}_max" for col in cols_stats] +
      [f"{col}_min" for col in cols_stats] +
      [f"{col}_q90" for col in cols_stats]
    )
    
    feature_rows = []
    window_id = 0

    for track_id in list_track_id:
        df = data[data['track_id'] == track_id]
        
        Tstart=df.iloc[0,4]
        Tend=df.iloc[-1,4]
        #Tend = datetime.strptime(Tend, "%Y-%m-%d %H:%M:%S")

        print("\n\nTrack ID: ", track_id)
        print("First timestamp: ", Tstart)
        print("Last timestamp: ", Tend)

        start_time = Tstart
        end_time = start_time + timedelta(seconds = seconds)

        while end_time < Tend:
            # print(start_time,end_time)

            windata = df[(df["time"] >= start_time) & (df["time"] < end_time)]

            f= []
            f= f + get_features_stats(windata,cols_stats)
            if not any(pd.isna(val) for val in f):
              row = [window_id] + f
              feature_rows.append(row)
              data.loc[(data['track_id'] == track_id) & (data['time'] >= start_time) & (data['time'] < end_time), 'window_id'] = int(window_id)
              window_id += 1
            
            start_time += timedelta(seconds=slide)
            end_time = start_time + timedelta(seconds=seconds)

    with open("features_windows.csv", "w", newline="") as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(header)
      writer.writerows(feature_rows)
            
    data['window_id'] = data['window_id'].astype('Int64')
    data.to_csv("dados_gps_analisados_with_window_id.csv", index=False)


grouping_by_time(15)