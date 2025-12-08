import pandas as pd
from data_cleaning import load_csv 
from datetime import datetime, timedelta
import math

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
    cols=["time","speed_mps","speed_kmh","acceleration_mps2","acceleration_kmh2","bearing_deg"]

    # Separate by track id
    df1 = data.groupby(['track_id']).count()
    list_track_id = df1['id'].keys().to_list()

    print(list_track_id)

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

        cols_stats=["speed_mps","speed_kmh","acceleration_mps2","acceleration_kmh2","bearing_deg"]

        while end_time < Tend:
            # print(start_time,end_time)

            windata = df[(df["time"] >= start_time) & (df["time"] < end_time)]

            f= []
            f= f + get_features_stats(windata,cols_stats)

            start_time += timedelta(seconds=slide)
            end_time = start_time + timedelta(seconds=seconds)


grouping_by_time(15)