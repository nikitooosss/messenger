from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str):
    hash = password_hash.hash(password=password)
    return hash


def verify_password(password: str, hash: str):
    valid = password_hash.verify(password=password, hash=hash)
    return valid
