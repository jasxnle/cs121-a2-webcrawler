import urllib.robotparser
from bs4 import BeautifulSoup
import urllib.request

class RobotChecker:
    def __init__(self, resp):
        self.website_url = resp.raw_response.url
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.robot_parser.set_url(self.website_url + "/robots.txt")
        self.robot_parser.read()

    def is_allowed(self, user_agent):
        return self.robot_parser.can_fetch(user_agent, self.website_url)

    def get_sitemap(self):
        try:
            with urllib.request.urlopen(self.website_url + "/sitemap.xml") as response:
                soup = BeautifulSoup(response, "html.parser")
                return soup
        except:
            return None
