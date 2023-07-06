import src.database 
import src.web_crawler 
import src.query_handler 


if __name__ == '__main__':
    db = src.database.Database()
    # db.drop_all_tables()

    crawler = src.web_crawler.Crawler(db)
    crawler.crawl()
    # test_query = input("Query: ")
    # query = Query(test_query, db)
    # query.get_search_results(100)
    # print(query.search_results)
