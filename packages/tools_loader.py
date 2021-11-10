#! /usr/bin/python3

import packages.json_handler
from packages.package_imports import *
from packages.static_paths import *
from packages.tools.amass import Amass
from packages.tools.gospider import GoSpider
from packages.tools.subdomainizer import Subdomainizer
from packages.tools.waybackurls import Waybackurls
from packages.tools.aquatone import Aquatone
from packages.tools.github_dorkers import GithubDorkers

paths = packages.json_handler.read_from(PATHS_JSON_FILE)

amass = Amass(paths["amass"])
subdomainizer = Subdomainizer(paths["SubDomainizer.py"])
aquatone = Aquatone(paths["aquatone"])
github_dorkers = GithubDorkers(paths["github-subdomains.py"])
gospider = GoSpider(paths["gospider"])
waybackurls = Waybackurls(paths["waybackurls"])