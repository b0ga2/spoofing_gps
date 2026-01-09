
M_SIZE_PER_ENTRY = 8

if __name__ == '__main__':
    a = [
-10.9393413858168,
-10.939341385765,
-10.93932394787612,
-10.93921056165612,
-10.93893897899615
    ]

    result = [(''.join([bin(int(c)).split('b')[1].rjust(4, '0') for c in str(a[entry_idx]).split('.')[1]]))[-M_SIZE_PER_ENTRY:] for entry_idx in range(len(a))]
    result = ''.join(result)
    result = ''.join([chr(int(result[i:i + 8], 2)) for i in range(0, len(result), 8)])
    print(result)
