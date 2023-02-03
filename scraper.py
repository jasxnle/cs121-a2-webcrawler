import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tokenizer import tokenize, computeWordFrequencies, mergeDictionary, generateHashes, getFinalHash, checkSimilarity

#
def checkSubdomain(url, resp):
    if resp.status != 200 or resp.raw_response.content == None:
        return (False, None)

    parsed = urlparse(url)
    subdomain = parsed.netloc.split('.', 1)

    if len(subdomain) > 1 and subdomain[1] in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
        return (True, subdomain)

    return (False, None)


def getLengthOfResponseContent(resp):
    if resp.status != 200 or resp.raw_response.content == None:
        return 0

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    return len(tokenize(soup.get_text()))

# Returns all the common words
def tokenizeResponseContent(resp, words):
    if resp.status != 200 or resp.raw_response.content == None:
        return words

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    return mergeDictionary(computeWordFrequencies(tokenize(soup.get_text())), words)

def scraper(url, resp):

    links = extract_next_links(url, resp)
    # use starting url and response to grab next links and data
    # create structure to store all links to visit
    

    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
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

    #checking if resp exists / is good to process
    #FIXME second condition
    if resp.status != 200 or resp.raw_response == None:
        return list()

    #FIXME
    #Add to config file later
    if len(resp.raw_response.content) > 4 * 1e9:
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    a_tags = soup.find_all("a")

    links = []
    for a in a_tags:
        link = a.get("href")

        #if link is empty
        if(not link):
            continue
        # if is relative link
        if (bool(urlparse(link).netloc) == False):
            if (link is not None and link[0] != "/"):
                link = "/" + link
            link = urljoin(url, link)

        if (bool(urlparse(link).fragment)):
            link = link.split('#')[0]

        if (is_valid(link)):
            links.append(link)


    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        #check if url contains valid domain to visit
        new_domain = parsed.netloc.split('.', 1)
        if len(new_domain) > 1 and new_domain[1] not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            return False
        # check if link is broken
        #
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
