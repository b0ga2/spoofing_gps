
M_SIZE_PER_ENTRY = 8

if __name__ == '__main__':
    # helloo (8)
    works = [
        -10.9393413858152,
        -10.9393413858149,
        -10.9393413858156,
        -10.9393413858156,
        -10.9393413858159,
        -10.9393413858159
    ]

    # test test in TPR for testing (16)
    no_works = [
        -10.9393413846117,
        -10.9393413845876,
        -10.9393413824628,
        -10.9393413842291,
        -10.9393413846048,
        -10.939341384331,
        -10.9393413824596,
        -10.9393413836882,
        -10.9393413824614,
        -10.939341384485,
        -10.9393413824628,
        -10.9393413842291,
        -10.9393413846121,
        -10.9393413844583
    ]

    result = ''
    for entry in works:
        result +=  bin(int(str(entry).split('.')[1])).split('b')[1][-M_SIZE_PER_ENTRY:].rjust(M_SIZE_PER_ENTRY,'0')

    decoded = [result[i:i+8] for i in range(0, len(result), 8)]
    for character in decoded:
        print(chr(int(character,2)), end='')
    print()
