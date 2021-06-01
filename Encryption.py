import key_gen

def ecb_encrypt(data, e, n,key_size):
    size_of_block = 64

    pixels = []
    for i in range(0, len(data), size_of_block):
        bytes_to_encrypt = bytearray(data[i: i + size_of_block])
        cipher_text = pow(int.from_bytes(bytes_to_encrypt, 'big'), e, n)
        block = cipher_text.to_bytes(int(n.bit_length()//8), 'big')
        for j in range(0, len(block)):
            pixels.append(block[j])

    return pixels
