import re
import nltk
import src.web_crawler
from nltk.corpus import stopwords
import math
from collections import defaultdict
import os


class Query:
    user_query = None
    prepared_query = None
    db = None
    index = []
    search_results = []

    def __init__(self, user_query, db) -> None:
        self.db = db
        self.user_query = user_query

        # Normalize and lemmatize the query
        temp_query = src.web_crawler.normalize_text(self.user_query)
        self.prepared_query = temp_query

        print('Prepared query: ' + self.prepared_query)

    def get_index(self) -> None:
        """
        Creates the index on which we can further select our results later on
        """
        print(self.prepared_query.split(' '))
        self.index = self.db.fetch_index(self.prepared_query.split(' '))

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
            (doc[0], doc[1], doc[2], doc[3], doc[4], doc[5], len(doc[6]) / max_rank, doc[7])
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
                    idf_scores[word] = math.log(doc_count / (1 + word_count_with_word))

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

    def get_search_results(self, amount):
        """
        Gets the top #amount search results from our database and ranks them based on multiple factors:
        In-link, tf-idf score and query-likelihood.

        Parameters:
        - amount (int): The amount of search results we want to have returned to us.

        Returns:
        The list of search results
        """
        self.get_index()

        if len(self.index) == 0:
            self.search_results = []
            return

        # At this point we apply some relevancy metrics and sort the results by importance
        self.link_based_ranking()
        tf_idf_scores = self.rank_documents(self.calculate_tf_idf())
        q_likelihood_scores = self.rank_likelihood()
        
        # combine and add the relevance scores with some weights added to each ranking
        self.index = [(doc[0], doc[1], doc[2], doc[3], doc[4], doc[5], 
                       0.2 * doc[6] + # link-based ranking score
                       0.4 * tf_idf_scores[index] + # tf-idf-based ranking score
                       0.4 * q_likelihood_scores[index], # query-likelihood ranking score
                       doc[7]) for index, doc in enumerate(self.index)]
        self.index.sort(key=lambda doc: doc[6], reverse=True)
        
        # considering runtime, adding diversity is too expensive for us at this stage

        # Set the results
        self.search_results = self.index[:amount]

        # save results to file
        result_dir = os.path.join(os.getcwd(), 'ResultLists')
        if not os.path.exists(result_dir):
            os.makedirs()
        os.chdir(result_dir)
        file_id = 0
        while os.path.exists('search_results_%s' % file_id):
            file_id += 1
        with open(f'search_results_{file_id}', 'w') as f:
            num = 1
            for result in self.search_results:
                f.write(str(num) + '    ' + result[1] + '    ' + result[6])
                num += 1
        print('Search results saved to file search_results_' + str(file_id))

        return self.search_results
