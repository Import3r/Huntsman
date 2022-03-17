#! /usr/bin/python3

from os import makedirs, path
from sys import argv
from packages.json_file_handler import FileJSON
from packages.common_utils import is_valid_domain_format, valid_github_token
import time


class Hunt:
    storage_dir_name = 'assets'
    inst_dir_name = 'installed_tools'
    wordlists_dir_name = 'wordlists'
    res_root_dir_name = 'huntsman_results'
    paths_json_file_name = '.inst_tools_paths.json'
    banner = """

    ▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
    ▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
    ▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

    """
    prompt_mess = """
    [!] usage:

        {} TARGET_DOMAINS GITHUB_TOKEN [DOMAIN_BLACKLIST]
            
    [!] comma separate multi-inputs
    """


    def __init__(self) -> None:
        self.storage_dir = self.storage_dir_name
        self.inst_tools_dir = path.join(self.storage_dir, self.inst_dir_name)
        self.wordlists_dir = path.join(self.storage_dir, self.wordlists_dir_name)
        self.res_root_dir = self.res_root_dir_name
        self.paths_json_file = FileJSON(path.join(path.dirname(argv[0]), self.paths_json_file_name))


    def check_arguments(self):
        # ensure correct usage of huntsman
        try:
            self.target_arg = argv[1]
            self.github_token = argv[2]
            try:
                self.blacklist_arg = argv[3]
            except:
                self.blacklist_arg = ''
        except:
            print(self.prompt_mess.format(argv[0]))
            exit()


    def validate_arguments(self):
        self.targets = set(self.target_arg.split(','))
        self.blacklist_targets = set(self.blacklist_arg.split(','))

        if not valid_github_token(self.github_token):
            print("[X] Faulty Github token, please provide a valid one")
            exit()

        for target in self.targets:
            if not is_valid_domain_format(target):
                print("[X] The target: '" + target + "' is not a valid domain format. Make sure to use a valid domain with no schema")
                exit()

        # checking for previous runs of 'Huntsman'
        if path.isdir(self.res_root_dir):
            print("[!] Results directory exists. Move or delete '" + self.res_root_dir + "' to initiate.")
            print("[!] Exiting to avoid loss of previous results...")
            exit()
        else:
            makedirs(self.res_root_dir)




