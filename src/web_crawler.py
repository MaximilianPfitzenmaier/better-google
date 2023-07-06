# imports
import requests
import re
import nltk
from langdetect import detect
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from rake_nltk import Rake
import time


class Crawler:
    initial_frontier = [
        # 'https://uni-tuebingen.deen/',
        # 'https://uni-tuebingen.de/en/facilities/central-institutions/university-sports-center/home/',
        'https://hoelderlinturm.de/english/',
        'https://www.tuebingen.de/en/',
        'https://hoelderlinturm.de/english/',
        'https://www.my-stuwe.de/en/',
        # # reichen solche datenbanken?

        # 'https://uni-tuebingen.de/en/',
        'https://civis.eu/en/about-civis/universities/eberhard-karls-universitat-tubingen',
        'https://tuebingenresearchcampus.com/en/',
        'https://is.mpg.de/en/',
        # # noch mehr guides, decken aber gut ab - zumal eh die einzelnen seiten idr nur auf deutsch sind
        'https://www.tripadvisor.com/Attractions-g198539-Activities-Tubingen_Baden_Wurttemberg.html',
        # 'https://www.medizin.uni-tuebingen.de/en-de/',
        'https://apps.allianzworldwidecare.com/poi/hospital-doctor-and-health-practitioner-finder?PROVTYPE=PRACTITIONERS&TRANS=Doctors%20and%20Health%20Practitioners%20in%20Tuebingen,%20Germany&CON=Europe&COUNTRY=Germany&CITY=Tuebingen&choice=en',
        'https://www.yelp.com/search?cflt=physicians&find_loc=T%C3%BCbingen%2C+Baden-W%C3%BCrttemberg%2C+Germany',
        'https://cyber-valley.de/',
        # 'https://www.tuebingen.mpg.de/84547/cyber-valley',
        'https://tuebingen.ai/',
        'https://www.bahnhof.de/en/tuebingen-hbf',
        'https://en.wikipedia.org/wiki/T%C3%BCbingen',
        'https://www.eml-unitue.de/',
        'https://wikitravel.org/en/T%C3%BCbingen',
        # # politics
        # # geograpy
        'https://www.engelvoelkers.com/en-de/properties/rent-apartment/baden-wurttemberg/tubingen-kreis/',
        'https://integreat.app/tuebingen/en/news/tu-news',
        'https://tunewsinternational.com/category/news-in-english/',  # news
        # # reichen solche guides?
        # 'https://guide.michelin.com/en/de/baden-wurttemberg/tbingen/restaurants',
    ]
    # our blacklist
    blacklist = ['https://www.tripadvisor.com/',
                 'https://www.yelp.com/',
                 ]

    db = None

    def __init__(self, db) -> None:
        self.db = db
        self.user_agent = 'TuebingenExplorer/1.0'
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        self.max_depth_limit = 1

        # If the frontier is empty, we load it with our initial frontier
        if self.db.check_frontier_empty():
            for link in self.initial_frontier:
                self.db.push_to_frontier(link)

    # Helper Functions
    def print_web_page(self, web_page):
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
        print(f"Normalized Title: {web_page['normalized_title']}")
        print(f"Keywords: {web_page['keywords']}")
        print(f"Description: {web_page['description']}")
        print(f"Normalized Description: {web_page['normalized_description']}")
        # print(f"Internal Links: {web_page['internal_links']}")
        # print(f"External Links: {web_page['external_links']}")
        # print(f"In Links: {web_page['in_links']}")
        # print(f"Out Links: {web_page['out_links']}")
        # print(f"Content: {web_page['content']}")
        print(f"Image URL: {web_page['img']}")

        print("--------------------")

    
    def add_internal_links_to_frontier(self, url, internal_links):
        """
        Adds all the internal links to the frontier array.
        Parameters:
        - url (BeautifulSoup): The BeautifulSoup url.
        - internal_links (list):  A list of visited internal URLs

        Returns:
        - None
        """

        for link in internal_links:
            if link.startswith("/") or link.startswith(url):
                if link.startswith("/"):
                    link = urljoin(url, link)
                self.frontier.append(link)

    
    def crawl_url(self, url):
        """
        Crawls a web page and extracts relevant information.

        Parameters:
        - url (str): The URL of the web page to crawl.
        - visited_urls (list): A list of visited URLs.
        - id (int): The web page ID starting with 0

        Returns:
        - None
        """

        print(f'LETS GO: {url}')
        # Code to measure the execution time
        time_start = time.time()
        if urljoin(url, '/') not in self.blacklist:
            try:

                # Make an HTTP GET request to the URL
                response = requests.get(url)
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                full_host = f"{parsed_url.scheme}://{host}" if f"{parsed_url.scheme}://{host}".endswith(
                    '/') else f"{parsed_url.scheme}://{host}/"

                # Check if the request is successful (status code 200)
                if response.status_code == 200:
                    # Check if crawling is allowed and if a delay is set
                    allowed_delay = is_crawling_allowed(url, self.user_agent)
                    allowed = allowed_delay[0]
                    crawl_delay = allowed_delay[1] if allowed_delay[1] else 0.5

                    if allowed:
                        # Use BeautifulSoup to parse the HTML content
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # only crawl the page content, if the content is english
                        if is_page_language_english(soup, url):

                            # get the sitemap for the host from the sitemap table
                            domain_internal_links = get_sitemap_from_host(
                                self, full_host)

                            domain_external_links = []

                            # Extract the title, keywords, description, internal/external links, content
                            index = None

                            title = get_page_title(soup)

                            normalized_title = get_normalized_title(
                                title) if title else None

                            description = get_description(soup)

                            normalized_description = get_normalized_description(
                                description) if description else None

                            links = get_internal_external_links(
                                soup, domain_internal_links, domain_external_links, full_host, self)

                            internal_links = links[0]
                            external_links = links[1]
                            domain_internal_links = links[2]

                            domain_external_links = links[3]

                            set_sitemap_to_host(
                                self, full_host, domain_internal_links)

                            content = get_page_content(soup)

                            keywords = get_keywords(
                                content, normalized_title, normalized_description)

                            in_links = []

                            out_links = []

                            img = get_image_url(soup, url)

                            # Create the web page object
                            web_page = create_web_page_object(
                                url,
                                index,
                                title,
                                normalized_title,
                                keywords,
                                description,
                                normalized_description,
                                internal_links,
                                external_links,
                                in_links,
                                out_links,
                                content,
                                img,
                            )

                            # Save to the database
                            entry = self.db.add_document(web_page)
                            web_page['id'] = entry[0]

                            #! Print the details of the web page
                            # self.print_web_page(web_page)

                            # Add the URL to the visited URLs list
                            self.db.add_visited_url(web_page['id'], url)

                            # Delay before crawling the next page
                            print(f'DELAY {crawl_delay}')
                            sleep(crawl_delay)

                            #! we dont push to frontier here. We push in get_internal_external_links after checking the content for each page
                            # Add all the internal links to the frontier
                            # for int_link in domain_internal_links:
                            #     if int_link is not url or int_link is not url[:-1]:
                            #         self.db.push_to_frontier(int_link)
                            # for ext_link in external_links:
                            #     self.db.push_to_frontier(ext_link)

                            # reset internal and external links array
                            # self.internal_links = []
                            # self.external_links = []

                        else:
                            print(
                                f"Not an English page: {url} or doesnt contain Tuebingen"
                            )
                    else:
                        print(
                            f"Error crawling: {url} | Allowed: {allowed} "
                        )
                else:
                    print(
                        f"Error crawling: {url} | Status: {response.status_code}"
                    )
            except Exception as e:
                print(f"Exception occurred while crawling: {url} | {e}")
        else:
            print(f"Domain blacklisted: {urljoin(url, '/')}")

        # Calculate the execution time
        time_end = time.time()
        execution_time = time_end - time_start

        # Print the execution time
        print(f"Execution time: {execution_time} seconds")

    # Start crawling all URL's in the frontier

    def crawl(self):
        while True:
            next_url = self.db.pop_frontier()
            if next_url is None:
                break
            self.crawl_url(next_url)


def get_sitemap_from_host(self, domain):
    """
    Gets the sitemap from the given domain.

    Parameters:
    - domain (string): The domain to retrieve the sitemap from.

    Returns:
    - list: The sitemap list of the domain, or an empty list if the host is not found.
    """
    try:
        sitemap = list(self.db.get_sitemap_from_domain(domain))
        return sitemap
    except Exception as e:
        print(f"Exception occurred while getting sitemap: {domain} | {e}")
        return []


def set_sitemap_to_host(self, domain, array_to_set):
    """
    Gets the sitemap from the given domain.

    Parameters:
    - domain
    - self

    Returns:
    - list: the sitemap list of the domain.
    """
    try:
        # update the domain_internal_links
        self.db.update_domain_sitemap(domain, array_to_set)

    except Exception as e:
        print(
            f"Exception occurred while setting sitemap: {domain} | {e}")


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
    if (
        html_tag
        and html_tag.has_attr('lang')
        and (html_tag['lang'].startswith('en') or html_tag['lang'].startswith('us'))
    ):
        return True
    elif match:
        return True
    elif detect(soup.getText()).startswith('en'):
        return True
    else:
        return False


# Crawler Functions
def create_web_page_object(
    url,
    index,
    title,
    normalized_title,
    keywords,
    description,
    normalized_description,
    internal_links,
    external_links,
    in_links,
    out_links,
    content,
    img,
):
    """
    Creates a web page object.

    Parameters:
    - id (int): The ID of the web page.
    - index (int | none): The index of the web page.
    - url (str): The URL of the web page.
    - title (str): The title of the web page.
    - normalized_title (str): The normalized title of the web page.
    - keywords (list): The keywords generated from the content.
    - description (str): The description from the description meta tag.
    - normalized description (str): The normalized description from the description meta tag.
    - internal_links (list): A list of internal links (URLs within the same domain).
    - external_links (list): A list of external links (URLs outside the current domain).
    - in_links (list): An empty list to store incoming links from other pages.
    - out_links (list): A list of URLs extracted from anchor tags on the page.
    - content (str): The plain text content of the web page.
    - img (str): The URL to the thumbnail.

    Returns:
    - dictionary: A dictionary representing the web page object.
    """

    return {
        # 'id': page_id,
        'url': url,
        'index': index,
        'title': title,
        'normalized_title': normalized_title,
        'keywords': keywords,
        'description': description,
        'normalized_description': normalized_description,
        'internal_links': internal_links,
        'external_links': external_links,
        'in_links': in_links,
        'out_links': out_links,
        'content': content,
        'img': img,
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


def get_normalized_title(title):
    """
    Normalize and lemmatize the given title.

    Parameters:
    - title (str): The input title to be normalized.

    Returns:
    - str: The normalized and lemmatized version of the title.
    """

    # Remove special characters and lowercase the content
    content = re.sub(r'[^\w\s]', '', title).lower()

    # Normalize German characters to English equivalents
    content = normalize_german_chars(content)

    # Tokenize the content
    tokens = word_tokenize(content)

    # Remove stopwords
    stopwords_set = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stopwords_set]

    # Lemmatize the content
    lemmatizer = WordNetLemmatizer()
    lemmatized_content = [lemmatizer.lemmatize(
        token) for token in filtered_tokens]

    # Convert the lemmatized content back to a string
    lemmatized_content_str = ' '.join(lemmatized_content)

    return lemmatized_content_str


def get_keywords(content, normalized_title, normalized_description):
    """
    Extracts the keywords from the content using the RAKE algorithm.

    Parameters:
    - content (str): The text content to extract keywords from.
    - normalized_title (str): The normalized_title to extract keywords from.
    - normalized_description (str): The normalized_description to extract keywords from.

    Returns:
    - list: The extracted keywords as a list of single words.
    """

    concat = ""
    if content is not None:
        concat += content + " "
    if normalized_title is not None:
        concat += normalized_title
    if normalized_description is not None:
        concat += normalized_description

    # Create an instance of the Rake object
    r = Rake()
    r.extract_keywords_from_text(concat)
    ranked_phrases_with_scores = r.get_ranked_phrases_with_scores()

    # Filter out phrases with more than one word
    single_words = [
        phrase
        for score, phrase in ranked_phrases_with_scores
        if len(phrase.split()) == 1
    ]

    # Deduplicate keywords (case-insensitive)
    unique_keywords = list(set(map(str.lower, single_words)))

    # Limit to the top single words
    keywords = unique_keywords

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


def get_normalized_description(description):
    """
    Normalize and lemmatize the given description.

    Parameters:
    - description (str): The input description to be normalized.

    Returns:
    - str: The normalized and lemmatized version of the description.
    """
    # Remove special characters and lowercase the content
    content = re.sub(r'[^\w\s]', '', description).lower()

    # Normalize German characters to English equivalents
    content = normalize_german_chars(content)

    # Tokenize the content
    tokens = word_tokenize(content)

    # Remove stopwords
    stopwords_set = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stopwords_set]

    # Lemmatize the content
    lemmatizer = WordNetLemmatizer()
    lemmatized_content = [lemmatizer.lemmatize(
        token) for token in filtered_tokens]

    # Convert the lemmatized content back to a string
    lemmatized_content_str = ' '.join(lemmatized_content)

    return lemmatized_content_str


def has_tuebingen_content(url):
    user_agent = 'TuebingenExplorer/1.0'
    try:
        response = requests.get(url)

        # Check if the request is successful (status code 200)
        if response.status_code == 200:
            is_allowed = is_crawling_allowed(url, user_agent)
            if is_allowed[0]:
                # Use BeautifulSoup to parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                if is_page_language_english(soup, url) and ('tuebingen' in str(soup) or 'Tuebingen' in str(soup) or 'tübingen' in str(soup) or 'Tübingen' in str(soup)):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f"Exception occurred while crawling: {url} | {e}")


def get_internal_external_links(soup, domain_internal_links, domain_external_links, host, self):
    """
    Extracts the internal and external links from a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.
    - url (str): The URL of the web page.

    Returns:
    - tuple: A tuple containing two lists:
        - list: The internal links (URLs within the same domain).
        - list: The external links (URLs outside the current domain).
    """
    # get the base url
    base_url = host
    internal_links = []
    external_links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('mailto:') and not href.startswith('tel:') and not href.startswith('javascript:') and not href.endswith('.jpg') and not href.endswith('.webp'):
            if href.startswith('http'):
                external_link = href
                if external_link not in external_links and base_url not in self.blacklist and is_page_language_english(soup, external_link):
                    external_links.append(external_link)
                    domain_external_links.append(external_link)
            elif not href.startswith('#') and not '#' in href:
                internal_link = base_url[:-1] + href

                #### check if we should push the url to the frontier
                # check if depth is fine
                if calculate_url_depth(internal_link) <= self.max_depth_limit:
                    # check if not in blacklist
                    if base_url not in self.blacklist:
                        # check if not in internal array
                        if base_url + 'en' in internal_link:
                            # check if the page content is english 
                            if is_page_language_english(soup, internal_link):
                                # check if the content has somthing todo with tuebingen
                                if has_tuebingen_content(internal_link):
                                    # check if not in sitemap
                                    if internal_link not in domain_internal_links:
                                        # frontier push here
                                        self.db.push_to_frontier(internal_link)

                else:
                    print(f'depth error: {internal_link}')
                # add all internal links to web_page_property
                internal_links.append(internal_link)

                # Add the URL to the domain sitemap
                domain_internal_links.append(internal_link)

    return (list(set(internal_links)), list(set(external_links)),  list(set(domain_internal_links)),  list(set(domain_external_links)))


def calculate_url_depth(url):
    """
    Calculates the depth of a URL based on the number of slashes in the path.
    If the URL contains '/en/' or '/english/' but not at the end, the depth is adjusted.
    https://example.com/ => depth = 0
    https://example.com/en/ => depth = 0
    https://example.com/page/ => depth = 1
    https://example.com/en/page/ => depth = 1

    Parameters:
    - url (str): The URL for which to calculate the depth.

    Returns:
    - int: The depth of the URL.
    """
    # Parse the URL to extract the path
    parsed_url = urlparse(url)
    
    path = parsed_url.path
    
    # add missing / 
    path = path if path.endswith('/') else path + '/'

    # Calculate the depth based on the number of slashes in the path
    depth = path.count("/") - 1

    # Check if the URL contains '/en/' or '/english/' but not at the end
    if "/en/" in path or "/english/" in path:
        depth -= 1

    return depth


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
    content = re.sub(r'<script[^>]*>[\s\S]*?<\/script>', ' ', content)

    # Remove style tags and their content
    content = re.sub(r'<style[^>]*>[\s\S]*?<\/style>', ' ', content)

    # Remove HTML comments
    content = re.sub(r'<!--[\s\S]*?-->', ' ', content)

    # Remove HTML tags
    content = re.sub(r'<.*?>', ' ', content)

    # Remove special characters (except "." and "@") and lowercase the content
    content = re.sub(r'[^\w\s.@]', '', content).lower()

    # Normalize German characters to English equivalents
    content = normalize_german_chars(content)

    #! enable later when we write our own keyword function
    # # Tokenize the content
    # tokens = word_tokenize(content)

    # # Remove stopwords
    # stopwords_set = set(stopwords.words('english'))
    # filtered_tokens = [token for token in tokens if token not in stopwords_set]

    # # Lemmatize the content
    # lemmatizer = WordNetLemmatizer()
    # lemmatized_content = [lemmatizer.lemmatize(
    #     token) for token in filtered_tokens]

    #! delete this later
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

    return lemmatized_content_str


def get_image_url(soup, url):
    """
    Extracts the og:twitter image URL or favicon URL from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.
    - url (str): The URL of the web page.

    Returns:
    - str: The og:image URL if found, otherwise the og:twitter image URL if found, otherwise the favicon URL, or an empty string if both are not found.
    """
    # Find the og:twitter image tag
    og_image_tag = soup.find(
        "meta", attrs={"property": "og:image"})

    # Find the og:twitter image tag
    twitter_image_tag = soup.find(
        "meta", attrs={"property": "twitter:imag"})

    # Find the favicon tag
    favicon_tag = soup.find("link", rel="icon")

    # Extract the og:image image URL
    if og_image_tag is not None:
        og_image_url = og_image_tag.get("content", "")
        if og_image_url:
            return og_image_url if og_image_url.startswith('http') else 'https:' + og_image_url

    # Extract the twitter:image URL
    elif twitter_image_tag is not None:
        og_image_url = twitter_image_tag.get("content", "")
        if og_image_url:
            return og_image_url if og_image_url.startswith('http') else urljoin(url, '/')[:-1] + og_image_url

    # Extract the favicon URL
    elif favicon_tag is not None:
        favicon_url = favicon_tag.get("href", "")
        if favicon_url:
            return urljoin(url, '/')[:-1] + favicon_url

    return ""
