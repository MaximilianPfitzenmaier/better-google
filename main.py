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


# app = Flask(__name__)

# # Configuring the template and static directories
# app.template_folder = "frontend/templates"
# app.static_folder = "frontend/static"


# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         query_text = request.form['query']
#         checkbox = request.form.get('checkbox', 'unchecked')

#         # Normalize and lemmatize the query
#         temp_query = web_crawler.normalize_text(query_text)
#         # Split the original string into a list of words
#         words = temp_query.split()

#         # Create a set to get unique words
#         unique_words_set = set(words)

#         # Convert the set back to a list to preserve the order
#         unique_words_list = list(unique_words_set)

#         # Join the unique words back into a string
#         keywords = ' '.join(unique_words_list)
#         keylength = len(str(keywords).split())

#         if (keylength > 9 and request.form['keytest'] == "0" and request.form['confirm'] == "0"):
#             return render_template('searchinput.html', keytest=keylength, query=query_text)
if __name__ == '__main__':
    time_start = time.time()

    # DATABASE
    db = database.Database(root_folder_path)
    # db.drop_all_tables()  # uncomment this to drop all your databse tables

    # db.create_keywords_table()
    # db = database.Database(root_folder_path)
    # CRAWLER uncomment the
    crawler = web_crawler.Crawler(db)
    # crawler.crawl()  # uncomment this to start crawling the url from the frontier.txt
    # crawler.create_inout_links()

    # QUERY
    query = query_handler.Query('tuebingen', db)
    # TODO before getting the urls take the query and call get_related_words from web_crawler to pull more pages
    # urls = db.get_all_urls_from_keywords(query.prepared_query)

    # returns (doc_id, url, title, description, img, ranking_score)
    # TODO parse url to get_serach_result() and fetch all the urls corrsponding to the keywords from the search from the database (inverted index)
    query.get_search_results(100)
    search_results = query.search_results

    # Calculate the execution time
    time_end = time.time()
    execution_time = (time_end - time_start) / 60
    #     wordlength = len(query_text.split())

    #     if checkbox != 'checked':
    #         return render_template('searchcards.html', query=query_text, results=search_results, execution_time=execution_time, wordlength=wordlength, keywords=keywords)
    #     else:
    #         return render_template('index.html', query=query_text, results=search_results, execution_time=execution_time, wordlength=wordlength, keywords=keywords)

    # return render_template('searchinput.html')


# if __name__ == '__main__':
#     app.run()
