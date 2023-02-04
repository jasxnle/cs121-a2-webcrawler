from utils import get_logger

from collections import defaultdict
# TODO: extract these "scraper" functions into here, they don't correspond with the scraper
from scraper import getLengthOfResponseContent, tokenizeResponseContent, checkSubdomain

# Do not make Stats static to mimick behavior of Frontier
class Stats(object):
    def __init__(self):
        self.logger = get_logger("STATS")
        self.STATS_FILE_NAME = "STATS_FILE.txt"
        self.uniquePages = 0
        self.longest_URL = ""
        self.longest_web_page = 0
        self.words = {}
        self.subdomains = defaultdict(int)

    def incrementUniquePages(self):
        self.uniquePages += 1

    def updateLongestWebPage(self, resp):
        length = getLengthOfResponseContent(resp)
        # max()
        if length > self.longest_web_page:
            self.longest_URL = resp.url
            self.longest_web_page = length

    def updateCommonWords(self, resp):
        self.words = tokenizeResponseContent(resp, self.words)

    def updateSubdomains(self, tbd_url, resp):
        # FIXME: can use resp.url instead of tbd_url?
        is_subdomain, subdomain = checkSubdomain(tbd_url, resp)
        if (is_subdomain):
            self.subdomains[subdomain] += 1



    def writeStatsToFile(self):
        # sorting 50 most common words
        sortFreq = dict(sorted(self.words.items(), key=lambda item: (-item[1], item[0])))
        commonWords = {k: sortFreq[k] for k in list(sortFreq)[:50]}

        def _getDictString(d):
            res = ""
            for k, v in d:
                res += (k + "=" + str(v) + "\n")
            return res


        # Write statistics to file
        with open(self.STATS_FILE_NAME, "w") as f:
            f.write(
                f"Num Unique Pages: {self.uniquePages}\n"
                f"\n\n"
                f"Longest Web Page: {self.longest_URL}\n"
                f"\n\n"
                f"Top 50 Common Words:\n"
                f"{_getDictString(commonWords)}\n"
                f"\n\n"
                f"Subdomains:\n"
                f"{_getDictString(self.subdomains)}\n"
            )
