import psycopg2

#jeder von uns erstellt eine database.txt in der die folgenden EIGENE werte stehen:
#host (idR localhost)
#database (zB porstgres)
#user (zB postgres)
#password (passwort für den user)

#die database.txt steht im .gitignore


def open_database():
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

cursor.execute("SELECT version()")
print(cursor.fetchone())

cursor.close()