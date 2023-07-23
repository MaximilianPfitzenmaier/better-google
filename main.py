import src.database
import src.web_crawler
import src.query_handler
import time
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query_text = request.form['query']
        checkbox = request.form.get('checkbox', 'unchecked')
        # ================= Test if to many keywords
        
        # Normalize and lemmatize the query
        temp_query = src.web_crawler.normalize_text(query_text)
        # Split the original string into a list of words
        words = temp_query.split()

        # Create a set to get unique words
        unique_words_set = set(words)

        # Convert the set back to a list to preserve the order
        unique_words_list = list(unique_words_set)

        # Join the unique words back into a string
        keywords = ' '.join(unique_words_list)
        keylength = len(str(keywords).split())
        print(len(str(keywords).split()))
        if(keylength > 9 and request.form['keytest'] == "0" and request.form['confirm'] == "0"):
            return render_template('searchinput.html', keytest=keylength, query=query_text)
        
        
         # =================
            
        time_start = time.time()
        db = src.database.Database()
        #db.drop_all_tables()

        #crawler = src.web_crawler.Crawler(db)
        #crawler.crawl()
        #crawler.create_inout_links()

        query = src.query_handler.Query(query_text, db)
        print(query.get_search_results)
        # returns (doc_id, url, title, description, img, ranking_score)
        query.get_search_results(100)
        search_results = query.search_results
        print(f'ergebnisse: {search_results}')

        # Calculate the execution time
        time_end = time.time()
        execution_time = (time_end - time_start) / 60
        wordlength = len(query_text.split())

        
        if checkbox != 'checked':
            return render_template('searchcards.html', query=query_text, results=search_results, execution_time=execution_time, wordlength=wordlength, keywords=keywords)
        else:    
            return render_template('index.html', query=query_text, results=search_results, execution_time=execution_time, wordlength=wordlength, keywords=keywords)


    return render_template('searchinput.html')


if __name__ == '__main__':
    app.run()

