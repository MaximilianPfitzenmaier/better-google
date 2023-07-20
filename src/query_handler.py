import re
import nltk
import src.web_crawler
from nltk.corpus import stopwords
import math
from collections import defaultdict


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

        # Split the original string into a list of words
        words = temp_query.split()

        # Create a set to get unique words
        unique_words_set = set(words)

        # Convert the set back to a list to preserve the order
        unique_words_list = list(unique_words_set)

        # Join the unique words back into a string
        result_string = ' '.join(unique_words_list)
        self.prepared_query = result_string

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

        Returns:
        None
        """
        max_rank = (
            len(max(self.index, key=lambda doc: len(doc[5]))[5])
            if len(self.index) > 0
            else 1
        )
        if max_rank == 0:
            max_rank = 1
        self.index = [
            (doc[0], doc[1], doc[2], doc[3], doc[4], len(doc[5]) / max_rank)
            for doc in self.index
        ]
        self.index.sort(key=lambda doc: doc[5], reverse=True)

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
        ranked documents
        """
        document_ids = [doc[0] for doc in self.index]
        document_url = [doc[1] for doc in self.index]
        document_title = [doc[2] for doc in self.index]
        document_desc = [doc[3] for doc in self.index]
        document_img = [doc[5] for doc in self.index]
        document_key = [doc[7] for doc in self.index]

        # Calculate document scores based on TF-IDF scores
        document_scores = []
        for score in tf_idf_scores:
            doc_score = sum(score.values())
            document_scores.append(doc_score)

        # Sort documents by score in descending order
        ranked_documents = sorted(
            range(len(document_scores)), key=lambda k: document_scores[k], reverse=True
        )

        # Rank documents
        final_ranked_documents = [
            (
                document_ids[i],
                document_url[i],
                document_title[i],
                document_desc[i],
                document_img[i],
                document_key[i],
                document_scores[i]
            )
            for i in ranked_documents
        ]

        return final_ranked_documents

    def rank_likelihood(self):
        """
           Rank a collection of documents relative to a query using the query likelihood model

           Returns:
           ranked documents
       """
        qwords = nltk.tokenize.word_tokenize(self.prepared_query)

        document_ids = [doc[0] for doc in self.index]
        document_url = [doc[1] for doc in self.index]
        document_title = [doc[2] for doc in self.index]
        document_desc = [doc[3] for doc in self.index]
        document_img = [doc[5] for doc in self.index]
        document_key = [doc[7] for doc in self.index]

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

        ranked_documents = sorted(
            range(len(document_scores)), key=lambda k: document_scores[k], reverse=True
        )

        final_ranked_documents = [
            (
                document_ids[i],
                document_url[i],
                document_title[i],
                document_desc[i],
                document_img[i],
                document_key[i],
                document_scores[i],
            )
            for i in ranked_documents
        ]

        return final_ranked_documents

    def get_search_results(self, amount):
        """
        Gets the top #amount search results from our database

        Parameters:
        - amount (int): The amount of search results we want to have returned to us.
        """
        self.get_index()

        # At this point we should apply some relevancy metrics and sort the results by importance
        # self.link_based_ranking()

        tf_idf_scores = self.calculate_tf_idf()

        ranked_documents = self.rank_documents(tf_idf_scores)
        print(self.rank_likelihood())

        # For now, I'll just return the results
        self.search_results = ranked_documents[:amount]
