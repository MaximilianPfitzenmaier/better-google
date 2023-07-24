# better-google


install all deps with: `pip install -r requirements.txt`

# Database

We're using PostgresSQL.
To connect, some parameters need to be supplied. Create a local database.txt file in the root of the project which contains host, database, user, password all on a new line. Example in README in MY SQL

# Frontier

Exists in a database table and can be kept between executions.

The initial frontier is made up of websites about that cover roughly the following topics:

- attractions
- food and drinks
- sport
- university
- clubs / night life
- medicine
- cyber valley
- traffic
- machine learning
- city
- public transportation
- politics
- geography
- living situation

Have an exclusion list of stuff we don't want to visit at all.

# Crawler

- Go through Frontier and pull urls
- Should be possible to stop and continue later
- Verify that the page contains Tübingen (or other variants like tuebingen)
- Save some important properties:
  - ID, Title, URL, Keywords, Description, InternLinks (sitemap), ExternLinks (rel=\_blank), inLinks = [], outlinks: $, content (plaintext after lemmatize/punctuation/lowercase/no tags etc.)
- Update frontier with new urls
- During testing we can optionally not update the frontier to limit our computation time
- To check: Uncertain properties like keywords and sitemap should be tested manually before we go all in

# After crawling

- calculate inlinks to each document by going through the ExternLinks and update each inLink entry

# Query processing

The query gets turned to lowercase and special characters are removed as well as german special characters normalized. Stopwords are also removed.
The prepared query is then used to gather the index based on whether any word from the query appears in the documents content, description, title or url.
