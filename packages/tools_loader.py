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

amass = Amass( paths["amass"] if "amass" in paths.keys() else "" )
subdomainizer = Subdomainizer( paths["SubDomainizer.py"] if "SubDomainizer.py" in paths.keys() else "" )
aquatone = Aquatone( paths["aquatone"] if "aquatone" in paths.keys() else "" )
github_dorkers = GithubDorkers( paths["github-subdomains.py"] if "github-subdomains.py" in paths.keys() else "" )
gospider = GoSpider( paths["gospider"] if "gospider" in paths.keys() else "" )
waybackurls = Waybackurls( paths["waybackurls"] if "waybackurls" in paths.keys() else "" )