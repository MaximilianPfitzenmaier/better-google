import re
import nltk
import backend.src.web_crawler as web_crawler
import math
from nltk.corpus import stopwords
from collections import defaultdict
import os


class Query:
    user_query = None
    prepared_query = None
    db = None
    index = []
    search_results = []

    def __init__(self, user_query, db, related) -> None:
        self.db = db
        self.user_query = user_query
        self.related = related

        # Normalize and lemmatize the query
        temp_query = web_crawler.normalize_text(self.user_query)

        # Split the original string into a list of words
        words = temp_query.split()

        # Create a set to get unique words
        unique_words_set = set(words)

        # Convert the set back to a list to preserve the order
        unique_words_list = list(unique_words_set)

        # call get_related_words to get more if no results where found for the query
        if (related):
            unique_words_list = web_crawler.get_related_words(
                unique_words_list, topn=2)

        # Join the unique words back into a string
        result_string = ' '.join(unique_words_list)
        self.prepared_query = result_string

    def get_index(self, urls) -> None:
        """
        Creates the index on which we can further select our results later on
        """
        self.index = self.db.fetch_index(urls)

    def link_based_ranking(self):
        """
        Creates a ranking based on the in_links of the documents in the index.
        """
        max_rank = (
            len(max(self.index, key=lambda doc: len(doc[6]))[6])
            if len(self.index) > 0
            else 1
        )
        if max_rank == 0:
            max_rank = 1
        self.index = [
            (doc[0], doc[1], doc[2], doc[3], doc[4],
             doc[5], len(doc[6]) / max_rank, doc[7], doc[8])
            for doc in self.index
        ]

    def calculate_tf_idf(self):
        """
        Calculates the TF-IDF scores for a given list of documents.

        Returns:
        List of TF_IDF scores for every document
        """
        documents = [doc[4] for doc in self.index]
        # Calculate term frequency (TF)
        tf_scores = []
        doc_word_counts = []
        for doc_content in documents:
            word_count = defaultdict(int)
            words = doc_content.split()
            for word in words:
                word_count[word] += 1
            doc_word_counts.append(word_count)

            tf_score = {}
            word_count_total = len(words)
            for word, count in word_count.items():
                tf_score[word] = count / word_count_total
            tf_scores.append(tf_score)

        # Calculate inverse document frequency (IDF)
        idf_scores = {}
        doc_count = len(documents)
        for word_count in doc_word_counts:
            for word in word_count.keys():
                if word not in idf_scores:
                    word_count_with_word = sum(
                        1 for wc in doc_word_counts if word in wc
                    )
                    idf_scores[word] = math.log(
                        doc_count / (1 + word_count_with_word))

        # Calculate TF-IDF scores
        tf_idf_scores = []
        for tf_score in tf_scores:
            tf_idf_score = {}
            for word, tf in tf_score.items():
                tf_idf_score[word] = tf * idf_scores[word]
            tf_idf_scores.append(tf_idf_score)

        return tf_idf_scores

    def rank_documents(self, tf_idf_scores):
        """
        Calculates the document scores based on the TF-IDF scores.
        It sums up the TF-IDF scores for each document and uses the sum as the document score.

        Returns:
        rank scores for each document
        """
        document_scores = []
        for score in tf_idf_scores:
            doc_score = sum(score.values())
            document_scores.append(doc_score)

        max_value = max(document_scores)
        if max_value == 0:
            max_value = 1
        document_scores = [x / max_value for x in document_scores]

        return document_scores

    def rank_likelihood(self):
        """
           Rank a collection of documents relative to a query using the query likelihood model

           Returns:
           rank scores for each doc in the index
       """
        qwords = nltk.tokenize.word_tokenize(self.prepared_query)
        document_scores = []

        for doc in self.index:
            dwords = nltk.tokenize.word_tokenize(doc[4])
            ddist = nltk.probability.FreqDist(dwords)

            score = 1.0
            len_doc = len(dwords)
            for word in qwords:
                tdist = ddist[word]
                score *= tdist / len_doc

            document_scores.append(round(score, 10))

        # normalize
        max_value = max(document_scores)
        if max_value == 0:
            max_value = 1
        document_scores = [x / max_value for x in document_scores]

        return document_scores

    def get_search_results(self, amount, urls):
        """
        Gets the top #amount search results from our database and ranks them based on multiple factors:
        In-link, tf-idf score and query-likelihood.

        Parameters:
        - amount (int): The amount of search results we want to have returned to us.

        Returns:
        The list of search results
        """
        self.get_index(urls)

        if len(self.index) == 0:
            self.search_results = []
            return

        # At this point we apply some relevancy metrics and sort the results by importance
        self.link_based_ranking()
        tf_idf_scores = self.rank_documents(self.calculate_tf_idf())
        q_likelihood_scores = self.rank_likelihood()

        # combine and add the relevance scores with some weights added to each ranking
        self.index = [(doc[0], doc[1], doc[2], doc[3], doc[4], doc[5],
                       0.2 * doc[6] +  # link-based ranking score
                       # tf-idf-based ranking score
                       0.4 * tf_idf_scores[index] +
                       # query-likelihood ranking score
                       0.4 * q_likelihood_scores[index],
                       doc[7], doc[8]) for index, doc in enumerate(self.index)]
        self.index.sort(key=lambda doc: doc[6], reverse=True)

        # considering runtime, adding diversity is too expensive for us at this stage

        # Set the results
        self.search_results = self.index[:amount]

        current_file = os.path.abspath(__file__)

        # Get the parent directory of the file (one folder up)
        this_folder = os.path.dirname(current_file)

        # Get the parent directory of the file's parent directory (two folders up)
        one_folders_up = os.path.dirname(this_folder)

        two_folders_up = os.path.dirname(one_folders_up)

        # save results to file
        result_dir = os.path.join(two_folders_up, 'resultLists')

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        os.chdir(result_dir)
        file_id = 0
        while os.path.exists('search_results_%s' % file_id):
            file_id += 1
        with open(f'search_results_{file_id}', 'w') as f:
            num = 1
            for result in self.search_results:
                f.write(str(num) + '    ' +
                        result[1] + '    ' + str(result[6]) + '\n')
                num += 1
        print('Search results saved to file search_results_' + str(file_id))

        return self.search_results
