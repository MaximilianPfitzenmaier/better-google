import re
import nltk
import src.web_crawler
from nltk.corpus import stopwords


class Query:
    user_query = None
    prepared_query = None
    db = None
    index = []
    search_results = []

    def __init__(self, user_query, db) -> None:
        self.db = db
        self.user_query = user_query

        # Should we even remove special characters?
        temp_query = re.sub(r'[^\w\s]', '', user_query).lower()
        temp_query = src.web_crawler.normalize_german_chars(user_query)

        tokens = nltk.tokenize.word_tokenize(temp_query)
        # remove stopwords
        stopwords_set = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token not in stopwords_set]

        self.prepared_query = ' '.join(filtered_tokens)

    def get_index(self) -> None:
        """
        Creates the index on which we can further select our results later on
        """
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
        self.index = [
            (doc[0], doc[1], doc[2], doc[3], doc[4], len(doc[5]) / max_rank)
            for doc in self.index
        ]
        self.index.sort(key=lambda doc: doc[5], reverse=True)

    def get_search_results(self, amount):
        """
        Gets the top #amount search results from our database

        Parameters:
        - amount (int): The amount of search results we want to have returned to us.
        """
        self.get_index()

        # At this point we should apply some relevancy metrics and sort the results by importance
        self.link_based_ranking()

        # For now, I'll just return the results
        self.search_results = self.index[:amount]
