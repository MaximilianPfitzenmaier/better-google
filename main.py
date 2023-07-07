import src.database
import src.web_crawler
import src.query_handler
import time


if __name__ == '__main__':
    time_start = time.time()
    db = src.database.Database()
    # db.drop_all_tables()

    crawler = src.web_crawler.Crawler(db)
    crawler.crawl()
    # test_query = input("Query: ")
    # query = Query(test_query, db)
    # query.get_search_results(100)
    # print(query.search_results)

    # Calculate the execution time
    time_end = time.time()
    execution_time = time_end - time_start
    # Print the execution time
    print(f"Execution time: {execution_time} seconds")
