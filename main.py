from database import Database


if __name__ == '__main__':
    db = Database()
    test_document = {
        "url": "testurl",
        "title": "testtitle",
        "keywords": [],
        "description": "",
        "internal_links": [],
        # "external_links": [],
        # "in_links": [],
        # "out_links": [],
        # "content": ""
    }
    db.insert(test_document)
    print(db.query("SELECT * FROM documents"))
