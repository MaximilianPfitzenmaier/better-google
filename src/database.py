import psycopg2

#                                   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
# jeder von uns erstellt lokal eine >>database.txt<< in der die folgenden EIGENE werte stehen für
# (dazwischen immer Enter):
# host (idR localhost)
# database (zB postgres)
# user (zB postgres)
# password (passwort für den user)

# die database.txt steht im .gitignore, so no worries


class Database:
    connection = None
    cursor = None

    def __init__(self) -> None:
        self.open_database()
        self.create_documents_table()
        self.create_visited_urls_table()
        self.create_frontier_table()
        self.create_sitemap_table()
        self.connection.commit()
        print('Database tables ready.')

    def __del__(self):
        self.cursor.close()

    def open_database(self):
        """
        Connect to the PostgreSQL database server
        """

        with open('src/database.txt', 'r') as f:
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

    def fetch_docs_by_id(self, doc_ids):
        """
        Fetch all the documents according to the list of ids given.

        Parameters:
        - doc_ids (int[]): An array of ids of documents.

        Returns:
        The list of documents gathered from our database.
        """
        sql = """
            SELECT id, url, title, description, img
            FROM documents
            WHERE id = ANY(%s)
        """
        self.cursor.execute(sql, (doc_ids,))
        # print(self.cursor.statusmessage)
        return self.cursor.fetchall()

    def fetch_index(self, search_words):
        """
        Fetch all the indices of documents which contain our search_words somewhere.

        Parameters:
        - search_words (str[]): An array of strings to search for

        Returns:
        The list of document ids that match our search.
        """
        sql = """
            WITH search_table AS (
                SELECT '%%' || unnest(%s) || '%%'
            )
            SELECT id
            FROM documents
            WHERE content ILIKE ANY (SELECT * FROM search_table)
                OR norm_title ILIKE ANY (SELECT * FROM search_table)
                OR norm_description ILIKE ANY (SELECT * FROM search_table)
                OR url ILIKE ANY (SELECT * FROM search_table)
        """
        self.cursor.execute(sql, (search_words,))
        # print(self.cursor.statusmessage)
        return [r[0] for r in self.cursor.fetchall()]

    def add_document(self, element):
        """
        Inserts a new entry into our documents table. It must be from a new url. Otherwise it gets rejected.

        Parameters:
        - element (dict): A dict of a new document entry.

        Returns:
        The new entry or None if an error was encountered.
        """
        sql = "INSERT INTO documents VALUES (default,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *"
        try:
            self.cursor.execute(
                sql,
                (
                    element.get("url"),
                    element.get("title", None),
                    element.get("normalized_title", None),
                    element.get("keywords", None),
                    element.get("description", None),
                    element.get("normalized_description", None),
                    element.get("internal_links", None),
                    element.get("external_links", None),
                    element.get("in_links", None),
                    element.get("out_links", None),
                    element.get("content", None),
                    element.get("img", None),
                ),
            )
            # print(self.cursor.statusmessage)
            self.connection.commit()
            return self.cursor.fetchone()
        except Exception as err:
            # print(err.args[0])
            self.connection.rollback()
            return

    def push_to_frontier(self, url):
        """
        Push a new value to the end of the frontier. Will only add unique values, duplicates will be rejected.

        Parameters:
        - url (string): The url to add to the frontier.
        """
        sql = """
            INSERT INTO frontier 
            SELECT %s
            WHERE NOT EXISTS (
                SELECT 1 
                FROM frontier
                WHERE url = %s
                UNION ALL
                SELECT 1
                FROM visited_urls
                WHERE url = %s )
        """

        self.cursor.execute(sql, (url, url, url))
        # print(self.cursor.statusmessage)
        self.connection.commit()

    def pop_frontier(self):
        """
        Get and remove an entry from the frontier.

        Returns:
        A url (string) or None if the frontier is empty.
        """
        sql = """
            DELETE FROM frontier
            WHERE url = (
                SELECT url
                FROM frontier
                LIMIT 1
            )
            RETURNING url
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)
        res = self.cursor.fetchone()
        self.connection.commit()
        return res if res is None else res[0]

    def check_frontier_empty(self):
        """
        Checks whether the frontier still has elements in it.

        Returns:
        True or False depending on whether the table has rows.
        """
        sql = """
            SELECT * FROM frontier LIMIT 1
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)
        res = self.cursor.fetchone()
        self.connection.commit()
        return True if res is None else False

    def is_url_visited(self, url):
        """
        Queries the visited_urls table and checks whether the url has been visited before.

        Parameters:
        - url (string): The url to check.

        Returns:
        - Tuple of (bool, timestamp)
        """
        sql = """
            SELECT last_visited
            FROM visited_urls
            WHERE url = %s
        """
        self.cursor.execute(sql, (url,))
        res = self.cursor.fetchone()
        return (False, None) if res is None else (True, res[0])

    def add_visited_url(self, doc_id, url):
        """
        Inserts the url into the visited url table with the current timestamp.

        Parameters:
        - doc_id (int): The id of the doc.
        - url (string): The url to insert.
        """
        sql = """
            INSERT INTO visited_urls VALUES (%s, %s, CURRENT_TIMESTAMP)
        """
        try:
            self.cursor.execute(sql, (doc_id, url))
            # print(self.cursor.statusmessage)
            self.connection.commit()
        except Exception as err:
            # print(err.args[0])
            self.connection.rollback()

    def get_sitemap_from_domain(self, domain):
        """
        Queries the visited_urls table and checks whether the url has been visited before.

        Parameters:
        - url (string): The url to check.

        Returns:
        - Tuple of (bool, timestamp)
        """
        sql = """
            SELECT links
            FROM sitemap
            WHERE url = %s
        """
        self.cursor.execute(sql, (domain,))
        res = self.cursor.fetchone()
        return res[0] if res else []

    def update_domain_sitemap(self, domain, domain_links):
        try:
            sql = """
                DELETE FROM sitemap 
                WHERE url = %s
            """
            self.cursor.execute(sql, (domain,))
            self.add_url_to_domains_sitemap(domain, domain_links)
            # print(self.cursor.statusmessage)
        except:
            self.add_url_to_domains_sitemap(domain, domain_links)

    def add_url_to_domains_sitemap(self, domain, domain_links):
        """
        Inserts the url into the visited url table with the current timestamp.

        Parameters:
        - domain (string): The domain of the doc.
        - domain_links (list): The url list to insert.
        """
        sql = """
            INSERT INTO sitemap VALUES (%s, %s)
        """
        try:
            # Convert the list to a comma-separated string
            domain_links_str = "{" + ", ".join(domain_links) + "}"
            self.cursor.execute(sql, (domain, domain_links_str))
            # print(self.cursor.statusmessage)
            self.connection.commit()
        except Exception as err:
            # print(err.args[0])
            self.connection.rollback()

    def create_documents_table(self):
        """
        Creates the documents table in our database if it does not exist already.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS documents (
                id               SERIAL PRIMARY KEY,
                url              TEXT NOT NULL UNIQUE,
                title            TEXT,
                norm_title       TEXT,
                keywords         TEXT[],
                description      TEXT,
                norm_description TEXT,
                internal_links   TEXT[],
                external_links   TEXT[],
                in_links         TEXT[],
                out_links        TEXT[],
                content          TEXT,
                img              BYTEA
            )
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)

    def create_visited_urls_table(self):
        """
        Creates the table with visited urls and their timestamps in our database if it does not exist already.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS visited_urls (
                id              INTEGER PRIMARY KEY,
                url             TEXT UNIQUE,
                last_visited    TIMESTAMP
            )
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)

    def create_sitemap_table(self):
        """
        Creates the table for all checked internal links from a domain.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS sitemap (
                url     TEXT UNIQUE,
                links   TEXT[]  
            )
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)

    def create_frontier_table(self):
        """
        Creates the table for our frontier which should hold the latest state of our crawling process.
        """
        sql = """
            CREATE TABLE IF NOT EXISTS frontier (
                url TEXT UNIQUE
            )
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)

    def drop_all_tables(self):
        """
        Drops all our tables. Intended to be used while developing. Do not call in code.
        """
        sql = """
            DROP TABLE IF EXISTS frontier;
            DROP TABLE IF EXISTS visited_urls;
            DROP TABLE IF EXISTS documents;
            DROP TABLE IF EXISTS sitemap;
        """
        self.cursor.execute(sql)
        # print(self.cursor.statusmessage)
        self.connection.commit()
