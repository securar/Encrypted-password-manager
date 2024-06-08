from Crypto.Cipher import AES
from string import ascii_letters

available_chars = ascii_letters.encode()
available_length = [16, 24, 32]


def generate_key(key_length: int) -> bytes:
    _key = b""
    with open("/dev/urandom", "rb") as file:
        while len(_key) < key_length:
            if (char := file.readline(1)) in available_chars:
                _key += char
    return _key


def encrypt(key: bytes, data: bytes) -> tuple[bytes, bytes, bytes]:
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    encrypted, tag = cipher.encrypt_and_digest(data)
    return encrypted, nonce, tag


def decrypt(key: bytes, encrypted: bytes, nonce: bytes, tag: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    decrypted = cipher.decrypt(encrypted)
    try:
        cipher.verify(tag)
        return decrypted
    except ValueError:
        raise ValueError("Invalid key or data corrupted")
