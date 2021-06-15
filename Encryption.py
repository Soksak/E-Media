import random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

def ecb_encrypt(data, e, n,key_size):
    block_size = key_size // 8 - 1
    encrypted_data = bytearray()
    after_iend_data = bytearray()

    for i in range(0, len(data), block_size):
        bytes_ = bytes(data[i:i + block_size])
        encrypt_int = pow(int.from_bytes(bytes_, 'big'), e, n)
        encrypt_bytes = encrypt_int.to_bytes(block_size + 1, 'big')
        after_iend_data.append(encrypt_bytes[-1])
        encrypt_bytes = encrypt_bytes[:-1]
        encrypted_data += encrypt_bytes

    return encrypted_data,after_iend_data

def ecb_decrypt(data, d, n ,key_size,after):
    decrypted_data = bytearray()
    block_size = key_size // 8 - 1
    after_index = 0

    for i in range(0, len(data), block_size):
        encrypted_bytes = data[i:i + block_size] + after[after_index].to_bytes(1, 'big')
        encrypted_int = int.from_bytes(encrypted_bytes, 'big')
        decrypted_int = pow(encrypted_int,d,n)
        decrypted_bytes = decrypted_int.to_bytes(block_size, 'big')
        decrypted_data += decrypted_bytes
        after_index += 1

    return decrypted_data

def cbc_encrypt(data,e,n,key_size):
    block_size = key_size // 8 - 1
    encrypted_data = bytearray()
    after_iend = bytearray()
    vector_IV = random.getrandbits(key_size)
    previous = vector_IV

    for i in range(0, len(data), block_size):
        bytes_ = bytes(data[i:i + block_size])
        previous = previous.to_bytes(block_size + 1, 'big')
        previous = int.from_bytes(previous[:len(bytes_)], 'big')
        xor = int.from_bytes(bytes_, 'big') ^ previous
        encrypt_int = pow(xor, e, n)
        previous = encrypt_int
        encrypt_bytes = encrypt_int.to_bytes(block_size + 1, 'big')
        after_iend.append(encrypt_bytes[-1])
        encrypt_bytes = encrypt_bytes[:-1]
        encrypted_data += encrypt_bytes

    return encrypted_data,previous,after_iend

def cbc_decrypt(data, d,n, key_size,vector_IV,after):

    decrypted_data = bytearray()
    block_size = key_size // 8 - 1
    previous = vector_IV
    after_index = 0

    for i in range(0, len(data), block_size):
        encrypted_bytes = data[i:i + block_size] + after[after_index].to_bytes(1, 'big')
        encrypted_int = int.from_bytes(encrypted_bytes, 'big')
        decrypted_int = pow(encrypted_int,d,n)
        previous = previous.to_bytes(block_size + 1, 'big')
        previous = int.from_bytes(previous[:block_size], 'big')
        xor = previous ^ decrypted_int
        decrypted_bytes = xor.to_bytes(block_size, 'big')
        decrypted_data += decrypted_bytes
        previous = int.from_bytes(encrypted_bytes, 'big')
        after_index += 1

    return decrypted_data


def library_encrypt(data,e,n,key_size):
    key = RSA.construct((n,e))
    encoder_library = PKCS1_v1_5.new(key)
    block_size = key_size // 16 - 1
    encrypted_data = bytearray()
    after_iend_data = bytearray()

    for i in range(0, len(data), block_size):
        bytes_ = bytes(data[i:i + block_size])
        encrypt_bytes = encoder_library.encrypt(bytes_)
        after_iend_data.append(encrypt_bytes[-1])
        encrypt_bytes = encrypt_bytes[:-1]
        encrypted_data += encrypt_bytes

    return encrypted_data, after_iend_data

