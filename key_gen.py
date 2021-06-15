import Crypto.Util.number as crypto



def generate_key(keysize: int):
    prime_size = keysize//2
    p = crypto.getPrime(prime_size)
    q = crypto.getPrime(prime_size)
    if p == q:
        raise ValueError("p and q can't be equal")
    n = p * q
    phi = (p - 1) * (q - 1)
    e = crypto.getRandomRange(1, phi)
    # Use Euclid's Algorithm to verify that e and phi(n) are comprime
    while (crypto.GCD(e, phi)) != 1:
        e = crypto.getRandomRange(1, phi)
    d = crypto.inverse(e, phi)
    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key




class RSA_key:
    def __init__(self,key_size):
        self.public_key, self.private_key = generate_key(key_size)