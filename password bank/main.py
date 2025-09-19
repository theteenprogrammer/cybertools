from cryptography.fernet import Fernet
from english_words import get_english_words_set
import random
import sqlite3
import os

# ---------------------------
# Encryption setup
# ---------------------------
key = b'iXEQzzk14y6m5r5-dpQg3_d3ndz_NOV_XfMeMKZvWQc='
cipher = Fernet(key)
DB_FILE = "backup.enc"
master_password = "1234"


def load_database():
    import tempfile
    conn = sqlite3.connect(":memory:")
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        # Write to temporary file
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(decrypted_data)
        tmp.close()
        disk_conn = sqlite3.connect(tmp.name)
        # Copy disk DB into memory
        disk_conn.backup(conn)
        disk_conn.close()
        os.remove(tmp.name)
    else:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collection (
                username TEXT,
                password BLOB,
                url TEXT UNIQUE
            );
        """)
    return conn


def save_database(conn):
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    disk_conn = sqlite3.connect(tmp.name)
    conn.backup(disk_conn)
    disk_conn.close()
    with open(tmp.name, "rb") as f:
        raw_bytes = f.read()
    encrypted = cipher.encrypt(raw_bytes)
    with open(DB_FILE, "wb") as f:
        f.write(encrypted)
    os.remove(tmp.name)



def generate_password():
    word_list = list(get_english_words_set(["web2"], lower=True))
    new_word = "".join(word_list[random.randint(0, 1000)] for _ in range(3))
    if len(new_word) < 13:
        print("Generated password not long enough")
    else:
        new_word += "".join(str(random.randint(0, 9)) for _ in range(3))
        new_word += "/#B"
        return new_word

def encryptpassword(password):
    return cipher.encrypt(password.encode())

def decryptpassword(password_blob):
    return cipher.decrypt(password_blob).decode()


def insertcredentials(conn, username, pwd, url):
    try:
        with conn:
            conn.execute(
                "INSERT INTO collection (username, password, url) VALUES (?, ?, ?)",
                (username, pwd, url)
            )
        print("Credentials inserted successfully.")
    except sqlite3.IntegrityError:
        print("A record for this URL already exists.")
    except sqlite3.OperationalError as e:
        print("Failed to execute SQL:", e)

def display_entries(conn):
    cursor = conn.execute("SELECT url FROM collection")
    results = [row[0] for row in cursor.fetchall()]
    if results:
        print(results)
    else:
        print("No credentials found.")

def retrieve_credentials(conn, url):
    cursor = conn.execute(
        "SELECT username, password FROM collection WHERE url = ?", (url,)
    )
    result = cursor.fetchone()
    if result:
        return result
    else:
        print("No credentials found for this URL.")
        return None

def delete_credentials(conn, url):
    with conn:
        cursor = conn.execute("DELETE FROM collection WHERE url = ?", (url,))
        if cursor.rowcount > 0:
            print(f"Deleted {cursor.rowcount} record(s) for URL: {url}")
        else:
            print("No credentials found for this URL.")


def addcredentials(conn):
    username = input("Enter username for website: ")
    url = input("Enter url of website: ")
    probe = input("Does a password already exist for this website? Y/N: ").upper()
    if probe == "Y":
        password = input("Enter password for website: ")
        insertcredentials(conn, username, encryptpassword(password), url)
    elif probe == "N":
        password = generate_password()
        print(f"Generated password: {password}")
        insertcredentials(conn, username, encryptpassword(password), url)
    else:
        print("Invalid input")

def get_credentials(conn):
    url = input("Enter the url of the credentials: ")
    cred = retrieve_credentials(conn, url)
    if cred:
        print("Username:", cred[0])
        print("Password:", decryptpassword(cred[1]))

def main_menu(conn):
    while True:
        print("\n=== Password Manager ===")
        print("1. Add credentials")
        print("2. Get credentials by URL")
        print("3. Display all entries")
        print("4. Delete entry")
        print("5. Exit")
        try:
            option = int(input("Choose an option: "))
        except ValueError:
            print("Invalid input")
            continue

        if option == 1:
            addcredentials(conn)
        elif option == 2:
            get_credentials(conn)
        elif option == 3:
            display_entries(conn)
        elif option == 4:
            url = input("Enter the url of the credentials: ")
            delete_credentials(conn, url)
        elif option == 5:
            print("Exiting program...")
            save_database(conn)
            conn.close()
            break
        else:
            print("Invalid option")


def main():
    password_input = input("Enter master password: ")
    if password_input != master_password:
        print("Wrong Password.")
        return
    conn = load_database()
    main_menu(conn)

if __name__ == "__main__":
    main()
