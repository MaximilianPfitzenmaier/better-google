# better-google

# Database

We're using PostgresSQL.
To connect, some parameters need to be supplied. Create a local database.txt file in the root of the project which contains host, database, user, password all on a new line. Example in database.py.

# Frontier

Will be an array consisting of urls that we plan to visit.
Resolve the following topics into urls we can use for a good initial frontier.

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

- Stemming + stop word removal
