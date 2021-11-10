#! /usr/bin/python3

from resources.packages import *
from resources.static_names import *
from resources.amass import Amass
from resources.gospider import GoSpider
from resources.subdomainizer import Subdomainizer
from resources.waybackurls import Waybackurls
from resources.aquatone import Aquatone
from resources.github_dorkers import GithubDorkers

with open(path.join(path.dirname(arg[0]), HM_PKGS_DIR ,PATHS_JSON_FILE), 'r') as json_file:
    paths = json.load(json_file)
    
    amass = Amass(paths["amass"])
    subdomainizer = Subdomainizer(paths["SubDomainizer.py"])
    aquatone = Aquatone(paths["aquatone"])
    github_dorkers = GithubDorkers(paths["github-subdomains.py"])
    gospider = GoSpider(paths["gospider"])
    waybackurls = Waybackurls(paths["waybackurls"])