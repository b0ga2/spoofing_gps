from data_cleaning import load_csv

if __name__ == '__main__':
    data = load_csv("go_track_trackspoints.csv")

    # size in bits
    M_SIZE_PER_ENTRY = 8
    M = "hello"
    M = ''.join([bin(ord(c)).split('b')[1].rjust(8, '0') for c in M])

    list_track_id = data['track_id'].unique().tolist()
    for track_id in list_track_id:
        df = data[data['track_id'] == track_id].sort_values('time')
        if df.empty:
            continue

        for entry_idx in range(len(df["latitude"])):
            entry_str = str(df["latitude"][entry_idx]).split('.')[1]

            # binary representation of the whole track id entry digit (after the period)
            b = list(''.join([bin(int(c)).split('b')[1].rjust(4, '0') for c in entry_str]))
            assert M_SIZE_PER_ENTRY < len(b)

            idx = M_SIZE_PER_ENTRY * entry_idx
            if idx >= len(M):
                break

            # get the corresponding M_SIZE_PER_ENTRY bits from the message (to be encoded)
            bits = M[idx:idx + M_SIZE_PER_ENTRY]

            # encode those bits
            b[-M_SIZE_PER_ENTRY:] = bits

            new_entry = float(str(df["latitude"][entry_idx]).split('.')[0] + '.' + ''.join([str(int(''.join(b[i:i+4]), 2)) for i in range(0, len(b), 4)]))
            print(new_entry)

        exit(0)()

        # # ''.join([bin(int(c)).split('b')[1].rjust(4, '0') for c in '0123456789'])
        # assert M_SIZE_PER_ENTRY <= 4
        # assert len(M) / M_SIZE_PER_ENTRY <= len(df["latitude"])
        # for entry_idx in range(len(df["latitude"])):
        #     entry_str = str(df["latitude"][entry_idx]).split('.')[1]
        #     # binary representation of the last track id entry digit
        #     b = bin(int(entry_str[-1])).split('b')[1].rjust(4, '0')
        #     # each character is 8 bits (we assume pure ascii)
        #     c_idx = int(M_SIZE_PER_ENTRY * entry_idx / 8)
        #     cb_idx = M_SIZE_PER_ENTRY * entry_idx % 8
        #     if c_idx >= len(M):
        #         break
        #     # get the corresponding 2 bits from the message (to be encoded)
        #     bits = bin(ord(M[c_idx])).split('b')[1].rjust(8, '0')[cb_idx:cb_idx + 2].rjust(2, '0')
        #     print(bits)
        # exit(0)
