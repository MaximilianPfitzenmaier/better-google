import src.database
import src.web_crawler
import src.query_handler
import time


if __name__ == '__main__':
    time_start = time.time()
    db = src.database.Database()

    crawler = src.web_crawler.Crawler(db)
    # crawler.crawl()
    crawler.create_inout_links()

    test_query = input("Query: ")
    query = src.query_handler.Query(test_query, db)

    # returns (doc_id, url, title, description, img, keywords, ranking_score, )
    print(query.get_search_results(100))

    # Calculate the execution time
    time_end = time.time()
    execution_time = (time_end - time_start) / 60
    # Print the execution time
    print(f"Execution time: {execution_time} min")
