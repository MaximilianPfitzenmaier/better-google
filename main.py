import backend.src.database as database
import backend.src.web_crawler as web_crawler
import backend.src.query_handler as query_handler
import time
import os
from flask import Flask, render_template, request


# Get the current script's file path
current_file = os.path.abspath(__file__)

# Get the directory of the current script
current_directory = os.path.dirname(current_file)

# Go up one level to reach the root folder
root_folder_path = os.path.dirname(current_directory)


app = Flask(__name__)

# Configuring the template and static directories
app.template_folder = "frontend/templates"
app.static_folder = "frontend/static"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        time_start = time.time()

        query_text = request.form['query']
        checkbox = request.form.get('checkbox', 'unchecked')

        unique_words_list = get_unique_words_list(query_text)

        # Join the unique words back into a string
        keywords = ' '.join(unique_words_list)
        keylength = len(str(keywords).split())

        if (keylength > 9 and request.form['keytest'] == "0" and request.form['confirm'] == "0"):
            return render_template('searchinput.html', keytest=keylength, query=query_text)

        # DATABASE
        db = database.Database()
        # db.drop_all_tables()  # uncomment this to drop all your databse tables
        db.create_keywords_table()

        # CRAWLER
        crawler = web_crawler.Crawler(db)
        crawler.crawl()  # uncomment this to start crawling the urls from the frontier.txt
        crawler.create_inout_links()

        # QUERY
        related = False
        search_results = get_results_from_databse(query_text, db, related)

        if len(search_results) <= 1:
            related = True
            search_results = get_results_from_databse(query_text, db, related)

        # Calculate the execution time
        time_end = time.time()
        execution_time = (time_end - time_start) / 60
        wordlength = len(query_text.split())

        if checkbox != 'checked':
            return render_template('searchcards.html', query=query_text, results=search_results, execution_time=execution_time, wordlength=wordlength, keywords=keywords)
        else:
            return render_template('index.html', query=query_text, results=search_results, execution_time=execution_time, wordlength=wordlength, keywords=keywords)

    return render_template('searchinput.html')


def get_results_from_databse(query_text, db, related):
    """
    get_results_from_database function description:
    Retrieves search results from the database for the provided query text.

    Parameters:
    - query_text (str): The query text to search for in the database.
    - db: The database instance.
    - related (bool): A flag indicating whether to search for related results.

    Returns:
    - list: A list of search results.
    """
    query = query_handler.Query(query_text, db, related)
    urls = db.get_all_urls_from_keywords(query.prepared_query)
    query.get_search_results(20, urls)
    search_results = query.search_results

    return search_results


def get_unique_words_list(query_text):
    """
    get_unique_words_list function description:
    Normalizes, lemmatizes, and retrieves a list of unique words from the provided query text.

    Parameters:
    - query_text (str): The query text to process.

    Returns:
    - list: A list of unique words from the query text.
    """
    # Normalize and lemmatize the query
    temp_query = web_crawler.normalize_text(query_text)
    # Split the original string into a list of words
    words = temp_query.split()

    # Create a set to get unique words
    unique_words_set = set(words)

    # Convert the set back to a list to preserve the order
    unique_words_list = list(unique_words_set)

    return unique_words_list


if __name__ == '__main__':
    app.run()
