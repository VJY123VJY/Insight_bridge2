import sqlite3
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()
AES_KEY = os.getenv("AES_KEY").encode()

def get_connection():
    conn = sqlite3.connect("db/bridge_buffer.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS buffer(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data BLOB NOT NULL
        )
    ''')
    conn.commit()
    return conn

def encrypt_data(data: bytes) -> bytes:
    f = Fernet(AES_KEY)
    return f.encrypt(data)

def decrypt_data(encrypted: bytes) -> bytes:
    f = Fernet(AES_KEY)
    return f.decrypt(encrypted)

def store_data(data_dict):
    conn = get_connection()
    c = conn.cursor()
    encrypted = encrypt_data(str(data_dict).encode())
    c.execute("INSERT INTO buffer(data) VALUES (?)", (encrypted,))
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT data FROM buffer")
    encrypted_rows = c.fetchall()
    decrypted = [eval(decrypt_data(row[0]).decode()) for row in encrypted_rows]
    conn.close()
    return decrypted
