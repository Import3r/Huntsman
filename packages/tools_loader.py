#! /usr/bin/python3

from packages.package_imports import *
from packages.static_paths import *
from packages.tools.amass import Amass
from packages.tools.gospider import GoSpider
from packages.tools.subdomainizer import Subdomainizer
from packages.tools.waybackurls import Waybackurls
from packages.tools.aquatone import Aquatone
from packages.tools.github_dorkers import GithubDorkers

with open(PATHS_JSON_FILE, 'r') as json_file:
    paths = json.load(json_file)
    
amass = Amass(paths["amass"])
subdomainizer = Subdomainizer(paths["SubDomainizer.py"])
aquatone = Aquatone(paths["aquatone"])
github_dorkers = GithubDorkers(paths["github-subdomains.py"])
gospider = GoSpider(paths["gospider"])
waybackurls = Waybackurls(paths["waybackurls"])