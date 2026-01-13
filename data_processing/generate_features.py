import os, math, sys
import pandas as pd
import numpy as np

# Radius of earth in meters
R_EARTH = 6371000 

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in meters between two Lat/Lon points."""
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R_EARTH * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculates bearing in degrees."""
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dLon = lon2_rad - lon1_rad

    y = math.sin(dLon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dLon)

    bearing_rad = math.atan2(y, x)
    return (math.degrees(bearing_rad) + 360) % 360

def process_gps_data(file_path, lat_col='latitude', lon_col='longitude', time_col='time', track_col='track_id'):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return None

    df = pd.read_csv(file_path)
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(by=[track_col, time_col]).reset_index(drop=True)

    # Shift columns for calculations
    df['lat_prev'] = df.groupby(track_col)[lat_col].shift(1)
    df['lon_prev'] = df.groupby(track_col)[lon_col].shift(1)
    df['time_prev'] = df.groupby(track_col)[time_col].shift(1)

    # 1. Distance & Time
    df['distance_m'] = np.where(df['lat_prev'].notna(), haversine_distance(df['lat_prev'], df['lon_prev'], df[lat_col], df[lon_col]), 0.0)
    df['time_diff_s'] = (df[time_col] - df['time_prev']).dt.total_seconds().fillna(0.0)

    # 2. Speed (m/s)
    df['speed_mps'] = np.where(df['time_diff_s'] > 0, df['distance_m'] / df['time_diff_s'], 0.0)

    # 3. Acceleration (m/s^2)
    df['speed_prev'] = df.groupby(track_col)['speed_mps'].shift(1)
    df['acceleration_mps2'] = np.where(df['time_diff_s'] > 0, (df['speed_mps'] - df['speed_prev']) / df['time_diff_s'], 0.0)

    # 4. NEW FEATURE: Jerk (m/s^3) - The derivative of acceleration
    df['accel_prev'] = df.groupby(track_col)['acceleration_mps2'].shift(1)
    df['jerk_mps3'] = np.where(df['time_diff_s'] > 0, (df['acceleration_mps2'] - df['accel_prev']) / df['time_diff_s'], 0.0)

    # 5. Bearing
    df['bearing_deg'] = df.apply(lambda row: calculate_bearing(row['lat_prev'], row['lon_prev'], row[lat_col], row[lon_col]) 
                                 if row['lat_prev'] is not np.nan else 0.0, axis=1)
    df['bearing_deg'] = df['bearing_deg'].replace(0, np.nan).groupby(df['track_id']).ffill().fillna(0)

    # Cleanup
    df = df.drop(columns=['lat_prev', 'lon_prev', 'time_prev', 'speed_prev', 'accel_prev'])
    return df

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python generate_features.py <input_csv> <output_csv>")
    else:
        df_final = process_gps_data(sys.argv[1])
        if df_final is not None:
            df_final.to_csv(sys.argv[2], index=False)
            print(f"Features generated with Jerk column added. Saved to {sys.argv[2]}")