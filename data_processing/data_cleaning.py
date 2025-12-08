import pandas as pd
import os

file_path = 'go_track_trackspoints.csv'


def load_csv(file_path: str):
    if not os.path.exists(file_path):
        print(f"ERRO: Ficheiro não encontrado no caminho: {file_path}")
        return None

    df = pd.read_csv(file_path)
    print(f"Dados carregados com sucesso. Total de linhas: {len(df)}")

    return df

# Remove tracks with less then X entries
def clean_data(min_num_of_entries: int):
    df = load_csv(file_path)

    df1 = df.groupby(['track_id']).count()

    df1 = df1[df1['id'] <= min_num_of_entries]

    # print(df1.head(10))

    list_track_id = df1['id'].keys().to_list()

    # print(list_track_id)

    df = df[~df['track_id'].isin(list_track_id)]

    df.to_csv('dados_gps_clean.csv', index=False)

clean_data(1)