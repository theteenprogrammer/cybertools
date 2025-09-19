from cryptography.fernet import Fernet
import sqlite3
import os


# Generate a key
key = b'iXEQzzk14y6m5r5-dpQg3_d3ndz_NOV_XfMeMKZvWQc='
cipher = Fernet(key)

master_password = "1234"


def encrypt_db():
    source_file = "my.db"
    destination_file = "backup.enc"

    with open(source_file, "rb") as src:
        plaintext = src.read()

    encrypted_data = cipher.encrypt(plaintext)

    with open(destination_file, "wb") as dest:
        dest.write(encrypted_data)

    os.remove(source_file)  # only unlinks file, not secure erase

encrypt_db()