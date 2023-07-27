# imports
import requests
import re
import nltk
import keybert
import threading
from langdetect import detect
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlparse, parse_qs
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from datetime import datetime
import threading
from translate import Translator as TranslateTranslator
from googletrans import Translator as GoogleTranslator
import os
import gensim.downloader as api


# Load the smaller pre-trained GloVe model
model = api.load("glove-wiki-gigaword-100")
# import goslate

# Create a thread-local instance of WordNet and a lock
wordnet_lock = threading.Lock()
db_lock = threading.Lock()
translation_lock = threading.Lock()
kw_model = keybert.KeyBERT()
# Define a thread subclass for crawling URLs


class CrawlThread(threading.Thread):
    """
        CrawlThread function description:
        This class represents a thread that is responsible for crawling a specific URL using the provided crawler.

        Parameters:
        - crawler: An instance of the Crawler class.
        - url: The URL to be crawled.

        Returns:
        - None
        """

    def __init__(self, crawler, url):
        """
        __init__ function description:
        Initializes a CrawlThread instance.

        Parameters:
        - crawler: An instance of the Crawler class.
        - url: The URL to be crawled.

        Returns:
        - None
        """
        super().__init__()
        self.crawler = crawler
        self.url = url

    def run(self):
        """
        run function description:
        Executes the crawling process for the provided URL using the associated Crawler.

        Parameters:
        - None

        Returns:
        - None
        """

        self.crawler.crawl_url(self.url)


class Crawler:

    initial_frontier = []

    # fill frontier with urls from frontier.txt
    # Get the current script's file path
    current_file = os.path.abspath(__file__)

    # Get the parent directory of the file (one folder up)
    one_folder_up = os.path.dirname(current_file)

    # Get the parent directory of the file's parent directory (two folders up)
    two_folders_up = os.path.dirname(one_folder_up)

    frontier = os.path.join(two_folders_up, 'data', 'frontier.txt')
    try:
        with open(frontier, 'r') as file:
            # Read all lines from the file into a list
            # rows = file.readlines()
            initial_frontier = [line.strip() for line in file.readlines()]

    except Exception as e:
        print(f"Error: {e}")

    # blacklist
    blacklist = [
        'https://www.tripadvisor.com/',
        'https://www.yelp.com/',
        'https://airtable.com/',
        'https://reddit.com/',
        'https://api.whatsapp.com/',
        'https://twitter.com/',
        'https://www.linkedin.com/',
        'https://apps.apple.com/',
        'https://play.google.com/',
        'https://careers.twitter.com/',
        'https://facebook.com/',
        'https://maps.google.com/',
        'https://create.twitter.com/',
        'https://is.mpg.de',
        'https://www.expedia.co.uk',
        'https://www.reservix.de/',
        'https://www.travelocity.com',
        'https://www.wotif.com/',
    ]

    db = None

    def __init__(self, db) -> None:
        """
        __init__ function description:
        Initializes an instance of the Crawler class.

        Parameters:
        - db: The database instance used to store crawled data.

        Returns:
        - None
        """
        current_file = os.path.abspath(__file__)

        # Get the parent directory of the file (one folder up)
        one_folder_up = os.path.dirname(current_file)

        # Get the parent directory of the file's parent directory (two folders up)
        two_folders_up = os.path.dirname(one_folder_up)

        nltk_data = os.path.join(two_folders_up, 'data', 'nltk')

        self.db = db
        self.user_agent = 'TuebingenExplorer/1.0'
        nltk.data.path.append(nltk_data)
        nltk.download('punkt', download_dir=nltk_data)
        nltk.download('wordnet', download_dir=nltk_data)
        nltk.download('stopwords', download_dir=nltk_data)
        nltk.download('averaged_perceptron_tagger',
                      download_dir=nltk_data)
        self.min_depth_limit = 0
        self.max_depth_limit = 0
        self.max_threads = 4
        self.base_crawl_delay = 2.0

        # If the frontier is empty, we load it with our initial frontier
        if self.db.check_frontier_empty():
            for link in self.initial_frontier:
                self.db.push_to_frontier(link)

    # Helper Functions

    def crawl_url(self, url):
        """
        crawl_url function description:
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
        if urljoin(url, '/') not in self.blacklist:
            # Make an HTTP GET request to the URL
            try:
                response = requests.get(url)
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                full_host = (
                    f"{parsed_url.scheme}://{host}"
                    if f"{parsed_url.scheme}://{host}".endswith('/')
                    else f"{parsed_url.scheme}://{host}/"
                )
            except:
                print(f"No request possible {url}")
                return  # Exit the function

            if full_host.endswith('.html/'):
                full_host = full_host[:-1]

            # Check if the request is successful (status code 200)
            if response.status_code == 200:
                # Check if crawling is allowed and if a delay is set
                allowed_delay = is_crawling_allowed(
                    self.base_crawl_delay, url, self.user_agent
                )
                allowed = allowed_delay[0]
                crawl_delay = (
                    allowed_delay[1] if allowed_delay[1] else self.base_crawl_delay
                )
                if allowed:
                    # Use BeautifulSoup to parse the HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # get the sitemap for the host from the sitemap table
                    sitemap = get_sitemap_from_host(self, full_host)
                    domain_external_links = []

                    try:
                        internal_links = []
                        external_links = []

                        links = get_internal_external_links(
                            soup,
                            sitemap,
                            domain_external_links,
                            full_host,
                            url,
                            self,
                        )

                        internal_links = links[0]
                        external_links = links[1]
                        sitemap = links[2]
                        domain_external_links = links[3]
                    except Exception as e:
                        print(
                            f"Exception occurred while intern extern : {url} | {e}")

                    set_sitemap_to_host(self, full_host, sitemap)

                    add_external_link_to_sitemap(self, domain_external_links)

                    if not has_tuebingen_content(url):
                        print(f"Not a Tübingen page: exiting {url}")
                        return  # Exit the function

                    index = None
                    title = ""
                    title = get_page_title(soup)

                    normalized_title = ""
                    normalized_title = normalize_text(title) if title else None

                    description = ""
                    description = get_description(soup)

                    normalized_description = ""
                    normalized_description = (
                        normalize_text(description) if description else None
                    )

                    content = get_page_content(soup)
                    normalized_content = normalize_text(
                        content) if content else None
                    limited_content = ""
                    limited_content = limit_string_to_50_words(
                        content)

                    keywords = []
                    all_related_words = []
                    try:
                        keywords = get_keywords(
                            normalized_content, normalized_title, normalized_description
                        )

                        keywords = get_related_words(keywords)
                    except Exception as e:
                        print(
                            f"Exception occurred while keywords: {url} | {e}")

                    in_links = []

                    out_links = []

                    img = list(get_image_url(soup, url))

                    # Create the web page object
                    web_page = create_web_page_object(
                        id,
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
                        limited_content,
                        normalized_content,
                        img,
                    )

                    # Save to the database
                    with db_lock:
                        try:
                            entry = self.db.add_document(web_page)
                            # If the document is in the db already, we get None back
                            web_page['id'] = None if entry is None else entry[0]
                        except Exception as e:
                            print(
                                f"Exception occurred while adding document: {url} | {e}\n"
                            )

                    with db_lock:
                        try:
                            # Add the URL to the visited URLs list
                            if entry is not None:
                                self.db.add_visited_url(web_page['id'], url)
                        except Exception as e:
                            print(
                                f"Exception occurred while adding visitied: {url} | {e}"
                            )

                    # Delay before crawling the next page
                    sleep(crawl_delay)

                    # else:
                    #     print(f"Not an English page: {url} or doesnt contain Tübingen")
                else:
                    print(f"Error crawling: {url} | Allowed: {allowed} ")
            else:
                print(
                    f"Error crawling: {url} | Status: {response.status_code}")
        else:
            print(f"Domain blacklisted: {urljoin(url, '/')}")

    #  Start crawling all URLs in the frontier
    def crawl(self):
        """
        crawl function description:
        Initiates the crawling process.

        Parameters:
        - None

        Returns:
        - None
        """
        threads = []
        while True:
            with db_lock:
                next_urls = self.db.get_from_frontier(self.max_threads)

                if next_urls is None:
                    break

            for url in next_urls:
                self.db.remove_from_frontier(url)

                thread = CrawlThread(self, url)
                thread.start()
                threads.append(thread)

            # Wait for all remaining threads to complete
            for thread in threads:
                thread.join()

            for thread in threads:
                threads.remove(thread)

    def create_inout_links(self):
        """
        create_inout_links function description:
        Populates the in_links and out_links fields in the database.

        Parameters:
        - None

        Returns:
        - None
        """
        self.db.create_inoutlinks()


def limit_string_to_50_words(input_string):
    """
    limit_string_to_50_words function description:
    Limits the input string to contain only the first 50 words.

    Parameters:
    - input_string (str): The input string to be limited.

    Returns:
    - str: The limited string containing the first 50 words.
    """

    # Split the input string into words
    words = input_string.split()

    # Take the first 50 words
    limited_words = words[:50]

    # Join the words back into a new string
    limited_string = " ".join(limited_words)

    return limited_string


def get_sitemap_from_host(self, domain):
    """
    get_sitemap_from_host function description:
    Gets the sitemap from the given domain.

    Parameters:
    - domain (string): The domain to retrieve the sitemap from.

    Returns:
    - list: The sitemap list of the domain, or an empty list if the host is not found.
    """

    with db_lock:
        try:
            sitemap = list(self.db.get_sitemap_from_domain(domain))
            return sitemap
        except Exception as e:
            print(f"Exception occurred while getting sitemap: {domain} | {e}")
            return []


def set_sitemap_to_host(self, domain, array_to_set):
    """
    set_sitemap_to_host function description:
    Sets the sitemap for the given domain in the database.

    Parameters:
    - domain (string): The domain to update the sitemap for.
    - array_to_set (list): The sitemap list to set for the domain.

    Returns:
    - None
    """

    with db_lock:
        try:
            # update the domain_internal_links
            self.db.update_domain_sitemap(domain, array_to_set)

        except Exception as e:
            print(f"Exception occurred while setting sitemap: {domain} | {e}")


def add_external_link_to_sitemap(self, domain_external_links):
    """
    add_external_link_to_sitemap function description:
    Adds the external links to the sitemap of their respective domains in the database.

    Parameters:
    - domain_external_links (list): A list of external links to be added to the sitemap.

    Returns:
    - None
    """
    # add the external links to the sitemap
    for external in domain_external_links:

        # get domain
        domain = urljoin(external, '/')
        domain = make_pretty_url(domain)

        # prepare link
        external = make_pretty_url(external)

        # call database functions
        # get sitemap
        sitemap = get_sitemap_from_host(self, domain)

        # add this link to the sitemap
        if external not in sitemap:
            sitemap.append(external)
            # write back sitemap
            set_sitemap_to_host(self, domain, sitemap)


def make_pretty_url(link):
    """
    make_pretty_url function description:
    Formats the input URL to have a consistent and pretty representation.

    Parameters:
    - link (str): The input URL to be formatted.

    Returns:
    - str: The formatted URL.
    """
    # prepare link
    if not link.endswith(".html") and not link.endswith(".aspx") and not link.endswith('.pdf'):
        link = (
            link
            if link.endswith("/")
            else link + "/"
        )
    return link


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


def is_text_english(text):
    """
    is_text_english function description:
    Checks if the provided text is in English.

    Parameters:
    - text (str): The input text to be checked.

    Returns:
    - bool: True if the text is in English, False otherwise.
    """
    text = str(text)

    try:
        language_code = detect(text)
        return language_code == 'en'
    except:
        return False


def create_web_page_object(
    id,
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
    normalized_content,
    img,
):
    """
    create_web_page_object function description:
    Creates a dictionary representing a web page object with various attributes.

    Parameters:
    - id (int): The web page ID.
    - url (str): The URL of the web page.
    - index (None or int): The index of the web page.
    - title (str): The title of the web page.
    - normalized_title (str): The normalized title of the web page.
    - keywords (list): The list of keywords associated with the web page.
    - description (str): The description of the web page.
    - normalized_description (str): The normalized description of the web page.
    - internal_links (list): The list of internal links on the web page.
    - external_links (list): The list of external links on the web page.
    - in_links (list): The list of incoming links to the web page.
    - out_links (list): The list of outgoing links from the web page.
    - content (str): The content of the web page.
    - normalized_content (str): The normalized content of the web page.
    - img (list): The list of image URLs on the web page.

    Returns:
    - dict: A dictionary representing the web page object with various attributes.
    """

    return {
        'id': 0,
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
        'normalized_content': normalized_content,
        'img': img,
    }


def is_crawling_allowed(base_crawl_delay, url, user_agent):
    """
    Checks if crawling is allowed for the given URL and user agent.

    Parameters:
    - url (str): The URL of the web page.
    - user_agent (str): The user agent string identifying the crawler.

    Returns:
    - (bool): True if crawling is allowed, False otherwise.
    - (float): The crawl delay in seconds if specified, base_crawl_delay otherwise.
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
            crawl_delay = base_crawl_delay
        return True, crawl_delay
    else:
        return False, base_crawl_delay


def get_page_title(soup):
    """
    get_page_title function description:
    Retrieves the page title from the provided BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.

    Returns:
    - str: The page title if found and in English, otherwise the translated title.
    """
    try:
        title = soup.title.string if soup.title else None

        # Remove URLs or sequences with non-word characters
        title = re.sub(r'https?://\S+|www\.\S+|\w*-\w*\.(\w+)', '', title)

        if title != None and is_text_english(title):
            return soup.title.string if soup.title else None
        elif title != None:
            return translate_to_english(title)
        else:
            return None

    except:
        return None


def get_related_words(keywords, topn=2):
    """
    Get related words for a given word using the pre-trained GloVe model.

    Parameters:
    - word (str): The word for which to find related words.

    Returns:
    - list: A list of related words.
    """
    related_keywords = []
    for word in keywords:
        try:
            # Find related words using GloVe's most_similar method
            related_words = model.most_similar(word, topn=topn)
            # Save the search word itself and its related words in the list
            related_keywords.append(word)
            related_keywords.extend(
                [related_word for related_word, _ in related_words])
        except KeyError:
            # Save the search word itself in case of an error
            related_keywords.append(word)

    # Remove duplicates while preserving the order
    final_keywords = []
    for keyword in related_keywords:
        keyword = normalize_text(keyword)
        if "https" in keyword or "http" in keyword or "www" in keyword or len(keyword) > 25:
            continue
        if keyword not in final_keywords:
            final_keywords.append(keyword)

    return final_keywords


def get_keywords(normalized_content, normalized_title, normalized_description):
    """
    Extracts the keywords from the content using the RAKE algorithm.

    Parameters:
    - normalized_content (str): The normalized_content to extract keywords from.
    - normalized_title (str): The normalized_title to extract keywords from.
    - normalized_description (str): The normalized_description to extract keywords from.

    Returns:
    - list: The extracted keywords as a list of single words.
    """

    concat = ""
    if normalized_content is not None:
        concat += normalized_content + " "
    if normalized_title is not None:
        concat += normalized_title
    if normalized_description is not None:
        concat += normalized_description

    keywords_a = kw_model.extract_keywords(concat, top_n=20)
    keywords = [normalize_text(key[0]) for key in keywords_a]

    return keywords


def translate_to_english(text):
    """
    translate_to_english function description:
    Translates the provided text from German to English.

    Parameters:
    - text (str): The text to be translated.

    Returns:
    - str: The translated text in English, or an empty string if translation fails.
    """
    with translation_lock:
        try:
            if text is None or not text:
                return ""
            else:
                translator = GoogleTranslator()
                translation = translator.translate(text, src='de', dest='en')
                return translation.text
        except:

            try:
                text = str(text)
                translator = TranslateTranslator(from_lang='de', to_lang='en')
                translation = translator.translate(text)
                return translation
            except:
                return ""


def get_description(soup):
    """
    get_description function description:
    Retrieves the description meta tag from the provided BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.

    Returns:
    - str: The content of the description meta tag if found and in English, otherwise the translated content.
    """
    try:
        description = soup.find('meta', attrs={'name': 'description'})
        if description['content'] != None and is_text_english(description):
            return description['content']
        else:
            return translate_to_english(description['content']) if description['content'] else None
    except:
        return None


def has_tuebingen_content(url):
    """
    has_tuebingen_content function description:
    Checks if the provided URL contains content related to Tübingen.

    Parameters:
    - url (str): The URL to be checked.

    Returns:
    - bool: True if the URL contains Tübingen-related content, False otherwise.
    """
    user_agent = 'TuebingenExplorer/1.0'
    base_crawl_delay = 2.0
    try:
        response = requests.get(url)

        allowed_delay = is_crawling_allowed(
            base_crawl_delay, url, user_agent)
        allowed = allowed_delay[0]

        if allowed:
            is_allowed = is_crawling_allowed(2.0, url, user_agent)
            if is_allowed[0]:
                # Use BeautifulSoup to parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                words_to_check = ['tuebingen',
                                  'Tuebingen',
                                  'tübingen',
                                  'Tübingen'
                                  ]
                for word in words_to_check:
                    if soup.find(text=lambda text: word in text):
                        return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f"Exception occurred while crawling: {url} | {e}")


def get_internal_external_links(
    soup, domain_internal_links, domain_external_links, host, url, self
):
    """
    get_internal_external_links function description:
    Retrieves internal and external links from the provided BeautifulSoup object and updates the link lists.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.
    - domain_internal_links (list): A list of internal links for the domain.
    - domain_external_links (list): A list of external links for the domain.
    - host (str): The host of the web page.
    - url (str): The URL of the web page.
    - self: The instance of the current class.

    Returns:
    - tuple: A tuple containing the updated internal and external link lists for the domain.
    """
    url = make_pretty_url(url)

    # get the base url
    base_url = host
    internal_links = []
    external_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if (
            href
            and not href.startswith('mailto:')
            and not href.startswith('tel:')
            and not href.startswith('javascript:')
            and not href.endswith('.jpg')
            and not href.endswith('.png')
            and not href.endswith('.gif')
            and not href.endswith('.webp')
            and not href.endswith('.pdf')
            and not href.endswith('.xml')
            and not '@' in href
            and not '?' in href
        ):

            if href.startswith('http'):
                external_link = href

                external_link = external_link if external_link.startswith(
                    'https') else external_link.replace("http://", "https://")

                #! add "/" if missing
                external_link = make_pretty_url(external_link)
                # check if we should push the url to the frontier
                # check if not in blacklist
                # if base_url not in self.blacklist:
                #     # check if depth is fine
                #     depth = calculate_url_depth(external_link)
                #     if depth <= self.max_depth_limit and depth >= self.min_depth_limit:
                #         # check if not in internal array
                #         if external_link != url:

                #             # check if not in sitemap
                #             domain = urljoin(external_link, '/')
                #             domain = make_pretty_url(domain)
                #             sitemap_from_this_host = get_sitemap_from_host(
                #                 self, domain)
                #             if external_link not in sitemap_from_this_host:

                #                 if external_link not in external_links:
                #                     with db_lock:
                #                         # frontier push here
                #                         # print(
                #                         #     f'add external link to frontier: {external_link}'
                #                         # )
                #                         self.db.push_to_frontier(external_link)

                # add all internal links to web_page_property
                external_links.append(external_link)

                # Add the URL to the domain sitemap
                # if not has_tuebingen_content(external_link):
                domain_external_links.append(external_link)

            elif not href.startswith('#') and not '#' in href:
                href = href if href.startswith('/') else '/' + href
                internal_link = base_url[:-1] + href
                #! add "/" if missing
                internal_link = make_pretty_url(internal_link)

                # check if we should push the url to the frontier
                # check if not in blacklist
                if base_url not in self.blacklist:
                    # check if depth is fine
                    depth = calculate_url_depth(internal_link)
                    if depth <= self.max_depth_limit and depth >= self.min_depth_limit:
                        # check if the internal link is the same url
                        if internal_link != url:
                            # check if not in sitemap
                            if internal_link not in domain_internal_links:
                                # if not has_tuebingen_content(internal_link):
                                with db_lock:
                                    # frontier push here
                                    self.db.push_to_frontier(
                                        internal_link)

                # add all internal links to web_page_property
                internal_links.append(internal_link)

                # Add the URL to the domain sitemap
                domain_internal_links.append(internal_link)

    return (
        list(set(internal_links)),
        list(set(external_links)),
        list(set(domain_internal_links)),
        list(set(domain_external_links)),
    )


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
    query = parsed_url.query

    path = parsed_url.path

    # add missing /
    path = path if path.endswith('/') else path + '/'

    # Calculate the depth based on the number of slashes in the path
    depth = path.count("/") - 1

    # Check if the URL contains '/en/' or '/english/' but not at the end
    if "/en/" in path or "/english/" in path:
        depth -= 1

    # Check if the URL has query parameters
    if query:
        depth += 1

        # Check if the query parameters contain a 'year' parameter
        query_params = parse_qs(query)
        year_param = query_params.get('year[]')
        if year_param:
            # Extract the first value of the 'year' parameter
            year = year_param[0]

            # Get the current year
            current_year = datetime.now().year
            # Check if the year is smaller than the current year - 3 years
            if int(year) < current_year - 3:
                return None  # Skip this URL

    return depth


def get_page_content(soup):
    """
    Extracts the plain text content of a web page from the given BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content.

    Returns:
    - str: content of the web page.
    """

    # Find all div elements
    div_elements = soup.find_all('div')

    # Remove div elements that contain 'Cookie' or 'cookie' in class, id, or content
    for div in div_elements:
        div_content = div.get_text() if div.get_text() else ''
        if div_content and ('Cookie' in div.get('class', '') or 'cookie' in div.get('class', '') or 'Cookie' in div.get('id', '') or 'cookie' in div.get('id', '')):
            div.decompose()

    # Get the remaining content
    content = str(soup)

    # Remove all classes and ids
    content = re.sub(
        r'(class|id|style|src|height|width|loading|iframe)="[^"]*"', '', content)

    # Remove style tags and their content
    content = re.sub(r'<style[^>]*>[\s\S]*?<\/style>', ' ', content)

    # Remove script tags and their content
    content = re.sub(r'<script[^>]*>[\s\S]*?<\/script>', ' ', content)

    # Remove forms and their content
    content = re.sub(r'<form[^>]*>[\s\S]*?<\/form>', ' ', content)

    # Remove table and their content
    content = re.sub(r'<table[^>]*>[\s\S]*?<\/table>', ' ', content)

    # Remove svg tags and their content
    content = re.sub(r'<svg[^>]*>[\s\S]*?<\/svg>', ' ', content)

    # Remove header tags and their content
    content = re.sub(r'<header[^>]*>[\s\S]*?<\/header>', ' ', content)

    # Remove nav tags and their content
    content = re.sub(r'<nav[^>]*>[\s\S]*?<\/nav>', ' ', content)

    # Remove breadcrumb tags and their content
    content = re.sub(r'<breadcrumb[^>]*>[\s\S]*?<\/breadcrumb>', ' ', content)

    # Remove footer tags and their content
    content = re.sub(r'<footer[^>]*>[\s\S]*?<\/footer>', ' ', content)

    # Remove HTML comments
    content = re.sub(r'<!--[\s\S]*?-->', ' ', content)

    # Remove HTML tags
    content = re.sub(r'<.*?>', ' ', content)

    # Remove special characters (except "." and "@") and lowercase the content
    content = re.sub(r'[^\w\s.@]', '', content).lower()

    # Split the content into words using spaces as the delimiter
    word_array = content.split()

    # Remove any leading/trailing whitespaces from each word in the array
    word_array = [word.strip() for word in word_array]

    # Remove empty strings from the array
    word_array = list(filter(None, word_array))

    # Join the elements in the array with an empty space in between
    final_string = " ".join(word_array)

    if final_string and not is_text_english(final_string):
        final_string = translate_to_english(final_string)

    return final_string


def get_image_url(soup, url):
    """
    get_image_url function description:
    Retrieves the image URL from the provided BeautifulSoup object.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object representing the web page content.
    - url (str): The URL of the web page.

    Returns:
    - list: A list containing the extracted og:image URL and favicon URL.
    """

    # Find the og:twitter image tag
    og_image_tag = soup.find("meta", attrs={"property": "og:image"})

    # Find the og:twitter image tag
    twitter_image_tag = soup.find("meta", attrs={"property": "twitter:imag"})

    # Find the favicon tag
    favicon_tag = soup.find("link", rel="icon")

    # Extract the favicon URL
    if favicon_tag is not None:
        favicon_url = favicon_tag.get("href", "")
        if favicon_url:
            favicon_url = urljoin(url, '/')[:-1] + favicon_url
    else:
        favicon_url = "empty"

    # Extract the og:image image URL
    if og_image_tag is not None:
        og_image_url = og_image_tag.get("content", "")
        if og_image_url:
            og_image_url = og_image_url if og_image_url.startswith(
                'http') else 'https:' + og_image_url

            return [og_image_url, favicon_url]

    # Extract the twitter:image URL
    elif twitter_image_tag is not None:
        og_image_url = twitter_image_tag.get("content", "")
        if og_image_url:
            og_image_url = og_image_url if og_image_url.startswith(
                'http') else urljoin(url, '/')[:-1] + og_image_url

            return [og_image_url, favicon_url]

    return ""


def pos_tagger(tag):
    """
    pos_tagger function description:
    Maps the part-of-speech tag to the appropriate WordNet POS tag.

    Parameters:
    - tag (str): The part-of-speech tag to be mapped.

    Returns:
    - None or str: The WordNet POS tag corresponding to the input tag, or None if the tag is not recognized.
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def normalize_text(input):
    """
    normalize_text function description:
    Normalizes the input text by removing special characters, lowercasing, normalizing German characters to English equivalents, tokenizing, removing stopwords, and lemmatizing.

    Parameters:
    - input (str): The input text to be normalized.

    Returns:
    - str: The normalized text.
    """
    # Check if the title is [null] or empty
    if input == "[null]" or not input:
        return None
    else:
        # Remove special characters and lowercase the content
        content = re.sub(r'[^\w\s]', '', input).lower()

        # Normalize German characters to English equivalents
        content = normalize_german_chars(content)

        # Tokenize the content
        tokens = word_tokenize(content)

        with wordnet_lock:

            # Remove stopwords
            stopwords_set = set(stopwords.words('english'))
            filtered_tokens = [
                token for token in tokens if token not in stopwords_set]

            # Get tags on each word
            token_pos_tags = nltk.pos_tag(filtered_tokens)
            wordnet_tag = map(lambda x: (
                x[0], pos_tagger(x[1])), token_pos_tags)
            lemmatized_content = []

            # Lemmatize the content
            lemmatizer = WordNetLemmatizer()

            for word, tag in wordnet_tag:
                if tag is None:
                    lemmatized_content.append(word)
                else:
                    lemmatized_content.append(lemmatizer.lemmatize(word, tag))

            # Convert the lemmatized content back to a string
            return ' '.join(lemmatized_content)
