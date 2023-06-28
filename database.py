import psycopg2

#                                   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
# jeder von uns erstellt lokal eine >>database.txt<< in der die folgenden EIGENE werte stehen für
# (dazwischen immer Enter):
# host (idR localhost)
# database (zB porstgres)
# user (zB postgres)
# password (passwort für den user)

# die database.txt steht im .gitignore, so no worries

class Database():
    connection = None
    cursor = None

    def __init__(self) -> None:
        self.open_database()
        self.create_table()
    
    def __del__(self):
        self.cursor.close()

    def open_database(self):
        """
        Connect to the PostgreSQL database server
        """

        with open('database.txt', 'r') as f:
            db = f.read().splitlines()

        self.connection = psycopg2.connect(
            host=db[0],
            database=db[1],
            user=db[2],
            password=db[3],
        )
        f.close()
        self.cursor = self.connection.cursor()

    def query(self, query):
        """
        Fetch entries from the database.
        TODO add prepared queries for common use cases

        Parameters:
        - query (str): The query to execute on the database.
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def insert(self, element):
        """
        Inserts a new entry into our documents table.
        
        Parameters:
        - element (dict): A dict of a new document entry.
        """
        sql = "INSERT INTO documents VALUES (default,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.execute(sql, (
            element.get('url'),
            element.get('title', None),
            element.get('keywords', None),
            element.get('description', None),
            element.get('internal_links', None),
            element.get('external_links', None),
            element.get('in_links', None),
            element.get('out_links', None),
            element.get('content', None)
            ))
        print(self.cursor.statusmessage)
        self.connection.commit()
    
    def create_table(self):
        """
        Creates the table in our database if it does not exist already.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS documents (
                id              SERIAL PRIMARY KEY,
                url             TEXT NOT NULL,
                title           TEXT,
                keywords        TEXT[],
                description     TEXT,
                internal_links  TEXT[],
                external_links  TEXT[],
                in_links        TEXT[],
                out_links       TEXT[],
                content         TEXT
            )
        """
        self.cursor.execute(sql)
        print(self.cursor.statusmessage)
