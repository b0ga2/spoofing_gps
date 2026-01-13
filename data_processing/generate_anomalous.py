from data_cleaning import load_csv
import sys

if __name__ == '__main__':
    data = load_csv(sys.argv[1])

    # size in bits
    M_SIZE_PER_ENTRY = 32
    M = "test test in TPR for testing"
    M = ''.join([bin(ord(c)).split('b')[1].rjust(8, '0') for c in M])

    list_track_id = data['track_id'].unique().tolist()
    rows = 0
    for track_id in list_track_id:
        df = data[data['track_id'] == track_id].sort_values('time')
        if df.empty:
            # print(f"{track_id} was discarted")
            continue

        for entry_idx in range(len(df["latitude"])):
            entry_str = str(df["latitude"].iloc[0]).split('.')[1]

            b = list(bin(int(entry_str)).split('b')[1])
            assert M_SIZE_PER_ENTRY < len(b) * 8

            idx = M_SIZE_PER_ENTRY * entry_idx
            if idx >= len(M):
                # print(f"{track_id} was broke")
                break

            # get the corresponding M_SIZE_PER_ENTRY bits from the message (to be encoded)
            bits = M[idx:idx + M_SIZE_PER_ENTRY]

            # encode those bits
            b[-M_SIZE_PER_ENTRY:] = bits

            new_entry = float(str(df["latitude"].iloc[0]).split('.')[0] + '.' + str(int(''.join(b), 2)))
            data.at[entry_idx + rows, "latitude"] = new_entry
        rows += len(df["latitude"]) 
    data.to_csv(sys.argv[2], index=False)
