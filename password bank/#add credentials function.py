#add credentials function
import sqlite3
from cryptography.fernet import Fernet


# Generate a key
key = b'iXEQzzk14y6m5r5-dpQg3_d3ndz_NOV_XfMeMKZvWQc='
cipher = Fernet(key)

def decryptpassword(new_word):
    decrypted_bytes = cipher.decrypt(new_word)  # don't decode here
    return decrypted_bytes.decode() 
    

def get_credentials(url):
    try:
        with sqlite3.connect('my.db') as conn:
            cursor = conn.cursor()
            select_stmt = """SELECT username, password FROM collection WHERE url = ?"""
            cursor.execute(select_stmt, (url,))
            result = cursor.fetchone()  # get the first matching record

            if result:
                username, password = result
                return username, password
            else:
                print("No credentials found for this URL.")
                return None
    except sqlite3.OperationalError as e:
        print("Failed to execute SQL:", e)
        return None

cred = get_credentials("url")
if cred:
    print("Username:", cred[0])
    print("Password:", decryptpassword(cred[1]))

