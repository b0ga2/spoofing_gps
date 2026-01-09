from data_cleaning import load_csv

def check_rounding_problem(n):
    # Check if the internal binary representation is slightly off
    # from the number you typed
    float_repr = repr(float(n))
    if str(n) != float_repr and not (str(n) + '0' in float_repr and 'e' not in float_repr):
        print(f"'{n}' likely has a rounding problem.")
        print(f"Stored internally as: {float_repr}")
        print(f"Displayed in Python as: {float(n)}\n")
    else:
        print(f"'{n}' is likely exact.\n")


if __name__ == '__main__':
    data = load_csv("go_track_trackspoints.csv")

    # size in bits
    M_SIZE_PER_ENTRY = 8
    M = "test test in TPR"
    M = ''.join([bin(ord(c)).split('b')[1].rjust(8, '0') for c in M])
    print(M)
    list_track_id = data['track_id'].unique().tolist()
    for track_id in list_track_id:
        df = data[data['track_id'] == track_id].sort_values('time')
        if df.empty:
            continue

        for entry_idx in range(len(df["latitude"])):
            entry_str = str(df["latitude"][entry_idx]).split('.')[1]

            # print(entry_str)
            # binary representation of the whole track id entry digit (after the period)
            # b = list(''.join([bin(int(c)).split('b')[1].rjust(4, '0') for c in entry_str]))
            # print(''.join(b))

            b = list(bin(int(entry_str)).split('b')[1])
            # print(bin(int(entry_str)).split('b')[1])

            assert M_SIZE_PER_ENTRY < len(b)

            idx = M_SIZE_PER_ENTRY * entry_idx
            if idx >= len(M):
                break

            # get the corresponding M_SIZE_PER_ENTRY bits from the message (to be encoded)
            bits = M[idx:idx + M_SIZE_PER_ENTRY]
            # print(bits)

            # encode those bits
            b[-M_SIZE_PER_ENTRY:] = bits

            # new_entry = float(str(df["latitude"][entry_idx]).split('.')[0] + '.' + ''.join([str(int(''.join(b[i:i+4]), 2)) for i in range(0, len(b), 4)]))
            new_entry = float(str(df["latitude"][entry_idx]).split('.')[0] + '.' + str(int(''.join(b),2)))
            print(new_entry)

            # check_rounding_problem(new_entry)

        exit(0)

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


