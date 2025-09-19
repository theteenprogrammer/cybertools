import sqlite3

sql_statements = [ 
    """CREATE TABLE IF NOT EXISTS collection (
            id INTEGER PRIMARY KEY, 
            username VARCHAR(50) NOT NULL, 
            password VARCHAR(50) NOT NULL, 
            url VARCHAR(50) NOT NULL

        );"""
]

# create a database connection
try:
    with sqlite3.connect('my.db') as conn:
        # create a cursor
        cursor = conn.cursor()

        # execute statements
        for statement in sql_statements:
            cursor.execute(statement)

        # commit the changes
        conn.commit()

        print("Tables created successfully.")
except sqlite3.OperationalError as e:
    print("Failed to create tables:", e)
