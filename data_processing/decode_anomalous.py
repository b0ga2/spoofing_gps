
M_SIZE_PER_ENTRY = 8

if __name__ == '__main__':
    a = [
-10.9393413858164,
-10.939341385829,
-10.9393239478643,
-10.93921056165,
-10.9389389789728,
-10.938543591154,
-10.9383460576357,
-10.9384484455027,
-10.93866607461,
-10.9389862284576,
-10.9393429131881,
-10.9396414360942,
-10.9398579141408,
-10.9400772901972,
-10.9403891021136,
-10.9407463806034
    ]

    result = ''

    for entry in a:

        print(bin(int(str(entry).split('.')[1])).split('b')[1][-M_SIZE_PER_ENTRY:].rjust(M_SIZE_PER_ENTRY,'0'))
        result +=  bin(int(str(entry).split('.')[1])).split('b')[1][-M_SIZE_PER_ENTRY:].rjust(M_SIZE_PER_ENTRY,'0')

    print(result)
    decoded = [result[i:i+8] for i in range(0, len(result), 8)]
    print(decoded)
    for character in decoded:
        print(chr(int(character,2)))
