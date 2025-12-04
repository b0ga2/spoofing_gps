import pandas as pd
import numpy as np
import os
import math

# Raio da Terra em metros (aproximado)
R_EARTH = 6371000 
CONVERSION_FACTOR_MPS_TO_KMH = 3.6 # 3600 segundos / 1000 metros = 3.6

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula a distância em metros entre dois pontos (Lat/Lon) usando a fórmula de Haversine."""
    
    # Converter graus para radianos
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    # Fórmula de Haversine
    a = np.sin(delta_phi / 2.0)**2 + \
        np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R_EARTH * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calcula o rumo (bearing) em graus (0-360) de P1 para P2."""
    
    # Converter graus para radianos
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dLon = lon2_rad - lon1_rad

    y = math.sin(dLon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dLon)

    bearing_rad = math.atan2(y, x)
    
    bearing_deg = math.degrees(bearing_rad)
    return (bearing_deg + 360) % 360

# --- FUNÇÃO PRINCIPAL ---

def process_gps_data(file_path, lat_col='latitude', lon_col='longitude', time_col='time', track_col='track_id'):
    """
    Carrega dados de GPS de um ficheiro CSV e calcula distância, tempo, velocidade (m/s e km/h), aceleração e rumo.
    """
    
    if not os.path.exists(file_path):
        print(f"ERRO: Ficheiro não encontrado no caminho: {file_path}")
        return None

    df = pd.read_csv(file_path)
    print(f"Dados carregados com sucesso. Total de linhas: {len(df)}")

    # 1. Pré-processamento e Ordenação
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(by=[track_col, time_col]).reset_index(drop=True)

    # 2. Criação de Colunas para Comparação (Shift)
    df['lat_prev'] = df.groupby(track_col)[lat_col].shift(1)
    df['lon_prev'] = df.groupby(track_col)[lon_col].shift(1)
    df['time_prev'] = df.groupby(track_col)[time_col].shift(1)

    # 3. Cálculo de Novos Campos

    ### 3.1. Distância (metros)
    df['distance_m'] = np.where(df['lat_prev'].notna(),
                               haversine_distance(df['lat_prev'], df['lon_prev'], 
                                                  df[lat_col], df[lon_col]), 
                               0.0)

    ### 3.2. Diferença de Tempo (segundos)
    df['time_diff_s'] = (df[time_col] - df['time_prev']).dt.total_seconds().fillna(0.0)

    ### 3.3. Velocidade (metros por segundo e km/h)
    
    # Velocidade em m/s
    df['speed_mps'] = np.where(df['time_diff_s'] > 0, 
                               df['distance_m'] / df['time_diff_s'], 
                               0.0)
                               
    # Conversão para km/h
    df['speed_kmh'] = df['speed_mps'] * CONVERSION_FACTOR_MPS_TO_KMH

    ### 3.4. Aceleração (m/s²)
    df['speed_prev'] = df.groupby(track_col)['speed_mps'].shift(1)
    df['acceleration_mps2'] = np.where(df['time_diff_s'] > 0,
                                       (df['speed_mps'] - df['speed_prev']) / df['time_diff_s'],
                                       0.0)
    # Conversão de aceleração para km/h²
    CONVERSION_FACTOR_MPS2_TO_KMH2 = 12960
    df['acceleration_kmh2'] = df['acceleration_mps2'] * CONVERSION_FACTOR_MPS2_TO_KMH2

    ### 3.5. Rumo (Bearing) (Graus)
    df['bearing_deg'] = df.apply(lambda row: calculate_bearing(row['lat_prev'], row['lon_prev'], row[lat_col], row[lon_col]) 
                                 if row['lat_prev'] is not np.nan else 0.0, 
                                 axis=1)

    # 4. Limpeza e Resultado
    df = df.drop(columns=['lat_prev', 'lon_prev', 'time_prev', 'speed_prev'])
    return df

# --- EXECUÇÃO ---

# 💡 ALTERE ESTE CAMINHO PARA ONDE O SEU FICHEIRO CSV ESTÁ LOCALIZADO
file_path = 'go_track_trackspoints.csv'

df_final = process_gps_data(file_path)

if df_final is not None:
    print("\n--- Primeiras Linhas do Resultado ---")
    # Mostrar as colunas relevantes, incluindo aceleração em km/h²
    print(df_final[['track_id', 'time', 'distance_m', 'time_diff_s', 'speed_mps', 'speed_kmh', 'acceleration_mps2', 'acceleration_kmh2', 'bearing_deg']].head(10))
    df_final.to_csv('dados_gps_analisados.csv', index=False)