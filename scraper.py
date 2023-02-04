import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tokenizer import tokenize, computeWordFrequencies, mergeDictionary
def checkSubdomain(url, resp):
    """This function checks if a url has a valid subdomain

    Args:
        url : Url that we want to check if it has a sub domain
        resp : response object containing status code and page content

    Returns:
        tuple : (True or False if a subdomain is present, full url with subdomain)
    """
    

    #checking is resp is a a valid link to parse
    if resp.status != 200 or resp is None or resp.raw_response is None or resp.raw_response.content is None :
        return (False, None)

    parsed = urlparse(url)
    subdomain = parsed.netloc.split('.', 1)

    # Report specified to find subdomains in the domain "ics.uci.edu" only
    if len(subdomain) > 1 and subdomain[1] in set(["ics.uci.edu"]):
        return (True, parsed.netloc)

    return (False, None)


def getLengthOfResponseContent(resp):
    """This function finds the largest web page crawled

    Args:
        resp : response object that contains stauts code and content of a url

    Returns:
        int : returns length for the response content
    """
    #checking is resp is a valid link to parse
    if resp.status != 200 or resp is None or resp.raw_response is None or resp.raw_response.content is None :
        return 0

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    return len(tokenize(soup.get_text()))

# Returns all the common words
def tokenizeResponseContent(resp, words):
    """this function is tokenizes the content of a webpage

    Args:
        resp : response object that contains stauts code and content of a url
        words : dictionary of current common words

    Returns:
        dictionary : merged diction of common words 
    """

    #checking if resp is a valid link to parse
    if resp.status != 200 or resp is None or resp.raw_response is None or resp.raw_response.content is None :
        return words

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    return mergeDictionary(computeWordFrequencies(tokenize(soup.get_text())), words)

def scraper(url, resp):
    """This function is used to scrape the webpage

    Args:
        url : Url that we want to check if it has a sub domain
        resp : response object containing status code and page content

    Returns:
        list : next links to crawl that are valid
    """
    links = extract_next_links(url, resp)
    # use starting url and response to grab next links and data
    # create structure to store all links to visit


    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    """Getting next links from a url

    Args:
        url : Url that we want to check if it has a sub domain
        resp : response object containing status code and page content

    Returns:
        list : next links to crawl
    """
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    # check for href attributes within response, can check if link should be crawled (is_valid)
    # convert relative urls to absolute urls

    # Max file size in GB
    MAX_FILE_SIZE = 4

    #checking if response is 200, resp is null , content is null
    if resp.status != 200 or resp is None or resp.raw_response is None or resp.raw_response.content is None :
        return list()

    # Do not scrape if file is above size threshold
    if len(resp.raw_response.content) > MAX_FILE_SIZE * 1e9:
        return list()

    # Scrape page and get all links as strings
    links = []
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    a_tags = soup.find_all("a")
    for a in a_tags:
        link = a.get("href")

        # if link is empty or is None
        if (not link or link is None):
            continue

        # if is relative link, correct faulty relative links
        # e.g. `href = "internal/path"` => `href = "/internal/path"`
        if (bool(urlparse(link).netloc) == False):
            if (link[0] != "/"):
                link = "/" + link
            link = urljoin(url, link)

        # filter out URLs with fragments
        if (bool(urlparse(link).fragment)):
            link = link.split('#')[0]

    return links

def is_valid(url):
    """checks is a url is a valid url to crawl

    Args:
        url : url that we are currently trying to crawl

    Returns:
        boolean : true if need to crawl, false not to crawl
    """
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        #checking if scheme is valid 
        if parsed.scheme not in set(["http", "https"]):
            return False

        # check if url contains valid domain to visit
        # FIXME: not correct lines
        # subdomain = parsed.netloc.split('.')[:-3]
        subdomain = parsed.netloc.split('.', 1)
        if len(subdomain) > 1 and subdomain[1] not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            return False

        # filter out any "mailto" links
        if re.match(r".*(mailto).*", parsed.path):
            return False

        # filter out problematic urls (calendar, swiki)
        if re.match(r".*(calendar|swiki|wiki).*", parsed.hostname):
            return False

        # check if link is valid extension
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|apk|war|img"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
