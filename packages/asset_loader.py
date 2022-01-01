#! /usr/bin/python3

from packages.json_handler import read_from
from packages.static_paths import PATHS_JSON_FILE
from packages.asset_modules.amass_tool import Amass
from packages.asset_modules.gospider_tool import GoSpider
from packages.asset_modules.subdomainizer_tool import Subdomainizer
from packages.asset_modules.waybackurls_tool import Waybackurls
from packages.asset_modules.aquatone_tool import Aquatone
from packages.asset_modules.github_dorkers_tool import GithubDorkers
from packages.asset_modules.massdns_tool import MassDNS
from packages.asset_modules.dns_resolvers_ip_list import DNSResolversList
from packages.asset_modules.assetfinder_tool import AssetFinder

paths = read_from(PATHS_JSON_FILE)

loaded_assets = {
    "amass" : Amass( paths["amass"] if "amass" in paths.keys() else "" ),
    "subdomainizer" : Subdomainizer( paths["SubDomainizer.py"] if "SubDomainizer.py" in paths.keys() else "" ),
    "aquatone" : Aquatone( paths["aquatone"] if "aquatone" in paths.keys() else "" ),
    "github_dorkers" : GithubDorkers( paths["github-subdomains.py"] if "github-subdomains.py" in paths.keys() else "" ),
    "gospider" : GoSpider( paths["gospider"] if "gospider" in paths.keys() else "" ),
    "waybackurls" : Waybackurls( paths["waybackurls"] if "waybackurls" in paths.keys() else "" ),
    "massdns" : MassDNS( paths["massdns"] if "massdns" in paths.keys() else "" ),
    "dns_resolvers_ip_list" : DNSResolversList( paths["dns_resolvers_ip_list"] if "dns_resolvers_ip_list" in paths.keys() else "" ),
    "assetfinder" : AssetFinder( paths["assetfinder"] if "assetfinder" in paths.keys() else "" )
}