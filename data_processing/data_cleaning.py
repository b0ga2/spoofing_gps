import pandas as pd
import os, sys

def load_csv(file_path: str):
    if not os.path.exists(file_path):
        print(f"ERRO: Ficheiro não encontrado no caminho: {file_path}")
        exit(1)

    df = pd.read_csv(file_path)
    print(f"Dados carregados com sucesso. Total de linhas: {len(df)}")

    return df

# remove tracks with less then x entries
def clean_data(min_num_of_entries: int):
    df = load_csv(sys.argv[1])

    df1 = df.groupby(['track_id']).count()
    df1 = df1[df1['id'] <= min_num_of_entries]

    list_track_id = df1['id'].keys().to_list()
    df = df[~df['track_id'].isin(list_track_id)]

    df.to_csv(sys.argv[2], index=False)

if __name__ == '__main__':
    clean_data(1)
