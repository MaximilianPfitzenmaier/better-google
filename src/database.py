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

    def fetch_index(self, search_words):
        """
        Fetch all the indices of documents which contain our search_words somewhere.

        Parameters:
        - search_words (str[]): An array of strings to search for

        Returns:
        The list of document ids that match our search.
        """
        sql = """
            WITH query_key(key) AS (
                SELECT unnest(%s)
                ),
                doc_key(id, key) AS (
                    SELECT id, unnest(keywords)
                    FROM documents
                )
            SELECT d.id, d.url, d.title, d.description, d.content, d.img, d.in_links, d.keywords
            FROM documents AS d
            WHERE d.id IN (SELECT DISTINCT d1.id
                           FROM doc_key AS d1, query_key AS q
                           WHERE d1.key ~* q.key);
        """
        self.cursor.execute(sql, (search_words,))
        # print(self.cursor.statusmessage)
        return self.cursor.fetchall()

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
                    element.get("normalized_description", None)
                    if element.get("normalized_description", None)
                    else [],
                    element.get("internal_links", []),
                    element.get("external_links", []),
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
            print('Error adding doc to db:\n' + err.args[0])
            self.connection.rollback()

            return

    def push_to_frontier(self, url):
        """
        Push a new value to the frontier. Will only add unique values, duplicates will be rejected.

        Parameters:
        - url (string): The url to add to the frontier.
        """
        sql = """
            INSERT INTO frontier 
            SELECT %s
            WHERE NOT EXISTS (
                SELECT 1
                FROM visited_urls
                WHERE url = %s )
        """
        try:
            self.cursor.execute(sql, (url, url))
            # print(self.cursor.statusmessage)
            self.connection.commit()
        except Exception as err:
            # print(err.args[0])
            self.connection.rollback()

    def get_from_frontier(self, amount):
        """
        Gets entries from the frontier.

        Parameters:
        - amount (int): The amount of entries we'd like to receive

        Returns:
        A list of url (string) or None if the frontier is empty.
        """
        sql = """
            SELECT DISTINCT ON (substring(url from '(?<=\/\/)[\w\d\.-]*'))
                url
            FROM frontier
            LIMIT %s
        """
        self.cursor.execute(sql, (amount,))
        # print(self.cursor.statusmessage)
        res = self.cursor.fetchall()
        self.connection.commit()
        return res if res is None else [x[0] for x in res]

    def remove_from_frontier(self, url):
        """
        Remove entries from the frontier.

        Parameters:
        - urls (string[]): The list of urls to remove.

        Returns:
        None
        """
        sql = """
            DELETE FROM frontier
            WHERE url = %s
        """
        self.cursor.execute(sql, (url,))
        self.connection.commit()
        return None

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

    def create_inoutlinks(self):
        """
        Update the in_links and out_links fields on all documents.

        Returns:
        None
        """
        sql = """
            UPDATE documents 
            SET
                out_links = (internal_links || external_links),
                in_links = subquery.aggregated_ids
            FROM (
                SELECT
                    d.id,
                    array_agg(d2.id) AS aggregated_ids
                FROM
                    documents AS d
                CROSS JOIN LATERAL (
                    SELECT id
                    FROM documents AS d2
                    WHERE d.url = ANY (d2.external_links)
                ) AS d2
                GROUP BY d.id
            ) AS subquery
            WHERE documents.id = subquery.id
        """
        self.cursor.execute(sql)
        print('Tried populating the in/out_links fields: ' + self.cursor.statusmessage)
        self.connection.commit()
        return None

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
                in_links         INT[],
                out_links        TEXT[],
                content          TEXT,
                img              TEXT
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
