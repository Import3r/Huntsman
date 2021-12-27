#! /usr/bin/python3

from packages.static_paths import HM_WORDLISTS_DIR
from packages.install_handler import update_install_path
from os import path, makedirs
import wget


class DNSResolversList:
    description = """

    a list of IP addresses for different dns resolvers, which are used for mass-resolving a list of domain names.
    
    """    
    asset_name = "dns_resolvers_ip_list"
    wordlist_file_name = "dns-resolvers.txt"
    wordlist_url = "https://raw.githubusercontent.com/BonJarber/fresh-resolvers/main/resolvers.txt"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.install_path = HM_WORDLISTS_DIR


    def install(self):
        makedirs(self.install_path, exist_ok=True)
        wordlist_path = path.join(self.install_path, self.wordlist_file_name)
        if path.exists(wordlist_path):
                update_install_path(self, wordlist_path)
        else:
            wget.download(self.wordlist_url, wordlist_path)
            if path.exists(wordlist_path):
                update_install_path(self, wordlist_path)            
            else:
                print("[X] Failed to download '" + self.asset_name + "' from'" + self.wordlist_url + "'\nexiting...")
                exit()
        