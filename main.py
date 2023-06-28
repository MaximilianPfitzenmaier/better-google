from database import Database
from web_crawler import Crawler


if __name__ == '__main__':
    db = Database()
    crawler = Crawler(db)
    crawler.crawl()
    print(db.query("SELECT * FROM documents"))
