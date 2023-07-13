from database import Database
from web_crawler import Crawler
from query_handler import Query


if __name__ == '__main__':
    db = Database()
    #db.drop_all_tables()
    crawler = Crawler(db)
    crawler.crawl()
    #test_query = input("Query: ")
    #query = Query(test_query, db)
    #query.get_search_results(100)
    #print(query.search_results)
