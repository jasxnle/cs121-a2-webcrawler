import urllib.robotparser

class RobotChecker:
    def __init__(self, url) -> None:
        self.website_url = url
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.have_robot = True
        try:
            self.robot_parser.set_url(self.website_url + "/robots.txt")
            self.robot_parser.read()
        except:
            self.have_robot = False

    def is_allowed(self, user_agent) -> bool:
        if self.have_robot:
            try:
                return self.robot_parser.can_fetch(user_agent, self.website_url)
            except:
                return False
        else:
            return True
        
        
    def get_sitemap(self) -> list:
        return self.robot_parser.site_maps()
        