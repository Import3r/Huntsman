#! /usr/bin/python3

from packages.json_handler import read_from
from packages.static_paths import PATHS_JSON_FILE
from packages.asset_modules.amass_tool import Amass
from packages.asset_modules.gospider_tool import GoSpider
from packages.asset_modules.subdomainizer_tool import Subdomainizer
from packages.asset_modules.waybackurls_tool import Waybackurls
from packages.asset_modules.aquatone_tool import Aquatone
from packages.asset_modules.github_dorkers_tool import GithubDorkers

paths = read_from(PATHS_JSON_FILE)

loaded_assets = {
    "amass" : Amass( paths["amass"] if "amass" in paths.keys() else "" ),
    "subdomainizer" : Subdomainizer( paths["SubDomainizer.py"] if "SubDomainizer.py" in paths.keys() else "" ),
    "aquatone" : Aquatone( paths["aquatone"] if "aquatone" in paths.keys() else "" ),
    "github_dorkers" : GithubDorkers( paths["github-subdomains.py"] if "github-subdomains.py" in paths.keys() else "" ),
    "gospider" : GoSpider( paths["gospider"] if "gospider" in paths.keys() else "" ),
    "waybackurls" : Waybackurls( paths["waybackurls"] if "waybackurls" in paths.keys() else "" )
}