import psycopg2

#                                   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
# jeder von uns erstellt lokal eine >>database.txt<< in der die folgenden EIGENE werte stehen für
# (dazwischen immer Enter):
# host (idR localhost)
# database (zB porstgres)
# user (zB postgres)
# password (passwort für den user)

# die database.txt steht im .gitignore, so no worries


def open_database():
    """
    Connect to the PostgreSQL database server

    :return: connection to execute sql queries
    """

    with open('database.txt', 'r') as f:
        db = f.read().splitlines()

    conn = psycopg2.connect(
        host=db[0],
        database=db[1],
        user=db[2],
        password=db[3],
    )
    f.close()
    return conn


conn = open_database()
cursor = conn.cursor()

# hier steht die eigentliche Query - oder SQL File, jenachdem für was wir uns am ende entscheiden
cursor.execute("SELECT version()")
print(cursor.fetchone())

cursor.close()
