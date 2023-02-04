from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

from collections import defaultdict
from tokenizer import checkSimilarity


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier

        self.STATS_FILE_NAME = "STATS_FILE.txt"         # FIXME: choose different name per worker to make thread-safe
        self.statistics_file = None
        self.uniquePages = 0
        self.words = {}
        self.longest_web_page = 0
        self.subdomains = defaultdict(int)
        self.longest_URL = ""

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            self.uniquePages += 1
            # TODO: check robots.txt to see if you can download the page
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            # TODO: Simhash: compare hashed resp of tbd_url to other hashes obtained
            #       from scraping. If similar to other hashes, do not scrape, download,
            #       or generate statistics.
            if (resp.status == 200 and resp is not None and checkSimilarity(resp)):
                self.logger.info(f"URL {tbd_url} found to be duplicate")
                continue

            scraped_urls = scraper.scraper(tbd_url, resp)

            # STATISTICS FOR REPORT
            # lenth of the url
            length = scraper.getLengthOfResponseContent(resp)
            # max()
            if length > self.longest_web_page:
                self.longest_URL = resp.url
                self.longest_web_page = length

            #finding common words
            self.words = scraper.tokenizeResponseContent(resp, self.words)

            is_subdomain, subdomain = scraper.checkSubdomain(tbd_url, resp)
            if (is_subdomain):
                self.subdomains[subdomain] += 1

            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        #sorting 50 most common words
        sortFreq = dict(sorted(self.words.items(), key=lambda item: (-item[1], item[0])))
        commonWords = {k: sortFreq[k] for k in list(sortFreq)[:50]}
        # Write statistics to file
        self.statistics_file = open(self.STATS_FILE_NAME, "w")
        self.statistics_file.write(f"Num Unique Pages: {self.frontier.uniquePages}\n")
        self.statistics_file.write("\n\n")
        self.statistics_file.write(f"Longest Web Page: {self.longest_URL}\n")
        self.statistics_file.write("\n\n")
        self.statistics_file.write(f"Top 50 Common Words:\n")
        for k, v in commonWords:
            self.statistics_file.write(k + "=" + str(v) +"\n")
        self.statistics_file.write("\n\n")
        self.statistics_file.write(f"Subdomains:\n")
        for k, v in self.subdomains:
            self.statistics_file.write(k + "=" + str(v) +"\n")
        self.statistics_file.close()
