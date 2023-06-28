# imports
import requests
import re
import nltk
from langdetect import detect
from time import sleep
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from rake_nltk import Rake

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


# starting frontier
frontier = [
    'https://hoelderlinturm.de/english/', 'https://www.tuebingen.de/en/'
    # reichen solche guides?
    'https://www.my-stuwe.de/en/', 'https://guide.michelin.com/en/de/baden-wurttemberg/tbingen/restaurants',
    # reichen solche datenbanken?
    'https://uni-tuebingen.de/en/facilities/central-institutions/university-sports-center/home/',
    'https://uni-tuebingen.de/en/', 'https://civis.eu/en/about-civis/universities/eberhard-karls-universitat-tubingen', 'https://tuebingenresearchcampus.com/', 'https://is.mpg.de/'
    # noch mehr guides, decken aber gut ab - zumal eh die einzelnen seiten idr nur auf deutsch sind
    'https://www.tripadvisor.com/Attractions-g198539-Activities-Tubingen_Baden_Wurttemberg.html',
    'https://www.medizin.uni-tuebingen.de/en-de/startseite', 'https://apps.allianzworldwidecare.com/poi/hospital-doctor-and-health-practitioner-finder?PROVTYPE=PRACTITIONERS&TRANS=Doctors%20and%20Health%20Practitioners%20in%20Tuebingen,%20Germany&CON=Europe&COUNTRY=Germany&CITY=Tuebingen&choice=en', 'https://www.yelp.com/search?cflt=physicians&find_loc=T%C3%BCbingen%2C+Baden-W%C3%BCrttemberg%2C+Germany',
    'https://cyber-valley.de/', 'https://www.tuebingen.mpg.de/84547/cyber-valley',
    'https://tuebingen.ai/', 'https://www.eml-unitue.de/',
    'https://en.wikipedia.org/wiki/T%C3%BCbingen', 'https://wikitravel.org/en/T%C3%BCbingen',
    'https://www.bahnhof.de/en/tuebingen-hbf',
    # politics
    # geograpy
    'https://www.engelvoelkers.com/en-de/properties/rent-apartment/baden-wurttemberg/tubingen-kreis/',
    'https://integreat.app/tuebingen/en/news/tu-news', 'https://tunewsinternational.com/category/news-in-english/'  # news
]

# init page id
page_id = 0

# our blacklist
blacklist = ['https://www.tripadvisor.com/', 'https://www.yelp.com/']

# cache to store processed content ( key: URL | value: web_page_object )
cache = {}
# TODO Also store this in databse

# Initialize the list of visited URLs
visited_urls = []
# TODO also store this list in database


# Helper Functions
def print_web_page(web_page):
    """
    Prints all details of the crawled web page.

    Parameters:
    - web_page (disctionary): The web page object.

    Returns:
    - None.
    """
    print(f"ID: {web_page['id']}")
    print(f"URL: {web_page['url']}")
    print(f"Title: {web_page['title']}")
    print(f"Keywords: {web_page['keywords']}")
    print(f"Description: {web_page['description']}")
    # print(f"Internal Links: {web_page['internal_links']}")
    # print(f"External Links: {web_page['external_links']}")
    # print(f"In Links: {web_page['in_links']}")
    # print(f"Out Links: {web_page['out_links']}")
    print(f"Content: {web_page['content']}")
    print("--------------------")


def normalize_german_chars(text):
    """
    Normalizes German characters in a given text to their English equivalents.

    Parameters:
    - text (str): The input text containing German characters.

    Returns:
    - str: The text with normalized German characters.
    """
    replacements = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss'
        # Add more replacements as needed
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def is_page_language_english(soup, url):
    """
    Checks if the language of a web page is English based on the lang attribute of the HTML tag.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - bool: True if the language is English, False otherwise.
    """
    # Convert the BeautifulSoup object to a string
    soup_str = str(soup)

    # Parse the HTML string using BeautifulSoup again
    inner_soup = BeautifulSoup(soup_str, 'html.parser')

    # Get the HTML tag
    html_tag = inner_soup.html

    # Match "/en/" or "=en" in the URL
    pattern = r"(/en/|=en)"

    # Search for the pattern in the URL
    match = re.search(pattern, url)

    # Check if the lang attribute is set to 'en'
    if html_tag and html_tag.has_attr('lang') and (html_tag['lang'].startswith('en') or html_tag['lang'].startswith('us')):
        return True
    elif match:
        return True
    elif detect(soup.getText()).startswith('en'):
        return True
    else:
        return False


def is_url_visited(url, visited_urls):
    """
    Checks if a URL has already been visited.

    Parameters:
    - url (str): The URL to check.
    - visited_urls (list): A list of visited URLs.

    Returns:
    - bool: True if the URL has already been visited, False otherwise.
    """
    return url in visited_urls


# Crawler Functions
def create_web_page_object(page_id, url, title, keywords, description, internal_links, external_links, in_links, out_links, content):
    """
    Creates a web page object.

    Parameters:
    - id (int): The ID of the web page.
    - url (str): The URL of the web page.
    - title (str): The title of the web page.
    - keywords (list): The keywords generated from the content.
    - description (str): The description from the description meta tag.
    - internal_links (list): A list of internal links (URLs within the same domain).
    - external_links (list): A list of external links (URLs outside the current domain).
    - in_links (list): An empty list to store incoming links from other pages.
    - out_links (list): A list of URLs extracted from anchor tags on the page.
    - content (str): The plain text content of the web page.

    Returns:
    - dictionary: A dictionary representing the web page object.
    """

    return {
        'id': page_id,
        'url': url,
        'title': title,
        'keywords': keywords,
        'description': description,
        'internal_links': internal_links,
        'external_links': external_links,
        'in_links': in_links,
        'out_links': out_links,
        'content': content
    }


def is_crawling_allowed(url, user_agent):
    """
    Checks if crawling is allowed for the given URL and user agent.

    Parameters:
    - url (str): The URL of the web page.
    - user_agent (str): The user agent string identifying the crawler.

    Returns:
    - (bool): True if crawling is allowed, False otherwise.
    - (float): The crawl delay in seconds if specified, 0.5 otherwise.
    """
    base_url = urljoin(url, '/')
    robots_url = urljoin(base_url, 'robots.txt')
    print(base_url)
    print(robots_url)

    # Fetch the Robots.txt file
    robot = RobotFileParser()
    robot.set_url(robots_url)
    robot.read()

    # Check if crawling is allowed for the given user agent
    if robot.can_fetch(user_agent, url):
        delay = robot.crawl_delay(user_agent)
        if delay:
            crawl_delay = delay
        else:
            crawl_delay = 0.5
        return True, crawl_delay
    else:
        return False, 0.5


def get_page_title(soup):
    """
    Extracts the title of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str or None: The title of the web page if found, otherwise None.
    """
    return soup.title.string if soup.title else None


def get_keywords(soup, content):
    """
    Extracts the keywords from the content using the RAKE algorithm.

    Parameters:
    - content (str): The text content to extract keywords from.

    Returns:
    - list: The extracted keywords as a list of single words.
    """
    # Create an instance of the Rake object
    r = Rake()
    r.extract_keywords_from_text(content)
    ranked_phrases_with_scores = r.get_ranked_phrases_with_scores()

    # Filter out phrases with more than one word
    single_words = [phrase for score, phrase in ranked_phrases_with_scores if len(
        phrase.split()) == 1]

    # Deduplicate keywords (case-insensitive)
    unique_keywords = list(set(map(str.lower, single_words)))

    # Limit to the top 20 single words
    keywords = unique_keywords[:20]

    return keywords


def get_description(soup):
    """
    Extracts the description from the description meta tag of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str or None: The description from the meta tag if found, otherwise None.
    """
    description = soup.find('meta', attrs={'name': 'description'})
    return description['content'] if description else None


def get_internal_external_links(soup):
    """
    Extracts the internal and external links from a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - tuple: A tuple containing two lists:
        - list: The internal links (URLs within the same domain).
        - list: The external links (URLs outside the current domain).
    """
    internal_links = []
    external_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            if href.startswith('http') or href.startswith('https'):
                external_links.append(href)
            else:
                internal_links.append(href)
    return (internal_links, external_links)


def get_page_content(soup):
    """
    Extracts the plain text content of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str: The lemmatized and normalized content of the web page.
    """
    # Get the remaining content
    content = str(soup)

    #! lets try our own regex the getText() function returns bullshit
    # Remove script tags and their content
    content = re.sub(
        r'<script[^>]*>[\s\S]*?<\/script>', ' ', content)
    
     # Remove style tags and their content
    content = re.sub(
        r'<style[^>]*>[\s\S]*?<\/style>', ' ', content)

    # Remove HTML comments
    content = re.sub(r'<!--[\s\S]*?-->', ' ', content)

    # Remove HTML tags
    content = re.sub(r'<.*?>', ' ', content)

    # Remove special characters (except "." and "@") and lowercase the content
    content = re.sub(r'[^\w\s.@]', '', content).lower()

    # Normalize German characters to English equivalents
    content = normalize_german_chars(content)

    # Tokenize the content
    tokens = word_tokenize(content)

    # Lemmatize the content
    lemmatizer = WordNetLemmatizer()
    lemmatized_content = []
    for token in tokens:
        lemma = lemmatizer.lemmatize(token)
        lemmatized_content.append(lemma)

    # Convert the lemmatized content back to a string
    lemmatized_content_str = ' '.join(lemmatized_content)
    # return test
    return lemmatized_content_str


def add_internal_links_to_frontier(url, internal_links):
    """
    Adds all the internal links to the frontier array.
    Parameters:
    - url (BeautifulSoup): The BeautifulSoup url.
    - internal_links (list):  A list of visited internal URLs

    Returns:
    - None
    """

    for link in internal_links:
        if link.startswith('/') or link.startswith(url):
            if link.startswith('/'):
                link = urljoin(url, link)
            frontier.append(link)


# Databse Functions
# TODO Databse functions here ...

def crawler(url, visited_urls, page_id):
    """
    Crawls a web page and extracts relevant information.

    Parameters:
    - url (str): The URL of the web page to crawl.
    - visited_urls (list): A list of visited URLs.
    - id (int): The web page ID starting with 0

    Returns:
    - None
    """
    if urljoin(url, '/') not in blacklist: 
        # Check if the URL has already been visited
        if is_url_visited(url, visited_urls):
            print(f"Already visited: {url}")
            return

        # Set the desired user agent for your crawler
        user_agent = 'TuebingenExplorer/1.0'

        # Check if crawling is allowed and if a delay is set
        allowed_delay = is_crawling_allowed(url, user_agent)
        allowed = allowed_delay[0]
        crawl_delay = allowed_delay[1] if allowed_delay[1] else 0.5

        # Make an HTTP GET request to the URL
        response = requests.get(url)
    
        # Check if the request is successful (status code 200)
        if response.status_code == 200 and allowed:
            # Use BeautifulSoup to parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # only crawl the page content, if the content is english
            if is_page_language_english(soup, url):

                # Extract the title, keywords, description, internal/external links, content
                title = get_page_title(soup)
                description = get_description(soup)
                internal_links = get_internal_external_links(soup)[0]
                external_links = get_internal_external_links(soup)[1]
                content = get_page_content(soup)
                keywords = get_keywords(soup, content)
                in_links = 0
                out_links = len(external_links)

                # Create the web page object
                web_page = create_web_page_object(
                    page_id, url, title, keywords, description, internal_links, external_links, in_links, out_links, content)

                #! Print the details of the web page
                print_web_page(web_page)
                
                # Add the URL to the visited URLs list
                visited_urls.append(url)

                # Add the URL to the cache
                cache[url] = web_page

                # Delay before crawling the next page
                sleep(crawl_delay)

                #! Add all the internal links to the frontier
                # add_internal_links_to_frontier(url, internal_links)

            else:
                print(f"Not an English page: {url}")
        else:
            print(f"Error crawling: {url} | Status: {response.status_code} | Allowed: {allowed} ")
    else:
        print(f"Domain blacklisted: {urljoin(url, '/')}")

# Start crawling all URL's in the frontier
for url in frontier:
    crawler(url, visited_urls, page_id)
    page_id += 1
