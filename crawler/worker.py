from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.statistics_file = None             # FIXME: will be thread-safe?
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
            # TODO: check robots.txt to see if you can download the page
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)

            # Statistics for report
            self.frontier.longest_web_page = max(self.frontier.longest_web_page, scraper.getLengthOfResponseContent(resp))
            self.frontier.words = scraper.tokenizeResponseContent(resp, self.frontier.words)

            is_subdomain, subdomain = scraper.checkSubdomain(tbd_url, resp)
            if (is_subdomain):
                self.frontier.subdomains[subdomain] += 1

            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        # record stats after done crawling
        self.statistics_file = open("STATS_FILE.txt", "w")
        self.statistics_file.write(f"Num Unique Pages: {self.frontier.uniquePages}\n")
        self.statistics_file.write(f"Longest Web Page: {self.frontier.longest_web_page}\n")
        self.statistics_file.write(f"Words: {self.frontier.words}\n")
        self.statistics_file.write(f"Subdomains: {self.frontier.subdomains}\n")
        self.statistics_file.close()
