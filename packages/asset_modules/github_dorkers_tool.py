#! /usr/bin/python3

from packages.static_paths import SUB_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from packages.common_utils import store_results, text_from_set_of_lines, set_of_lines_from_text, is_valid_domain_format
from os import path
from sys import executable
from subprocess import Popen, run, STDOUT, PIPE
import git


class GithubDorkers:
    asset_name = "github-subdomains.py"
    req_file_name = "requirements3.txt"
    output_file_name = "subdomains.github"
    remote_repo_name = "github-search"
    remote_repo_url = "https://github.com/gwen001/github-search.git"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_file = path.join(SUB_HOUND_RES_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.req_file = path.join(self.install_path, self.req_file_name)
        self.output_buffer = ""
        self.results_set = set()


    def install(self):
        if not path.exists(self.install_path):
            git.cmd.Git(INST_TOOLS_DIR).clone(self.remote_repo_url)
        run([executable, "-m", "pip", "install", "-r", self.req_file], stderr=STDOUT)
        
        if path.exists(path.join(self.install_path, self.asset_name)):
            update_install_path(self, path.join(self.install_path, self.asset_name))
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def enumerator_proc(self, target, gh_token):
        return Popen(f"{self.asset_path} -t {gh_token} -d {target}", shell=True, stdout=PIPE)


    def thread_handler(self, targets, gh_token):
        print("[+] Dorking GitHub for subdomains...")
        for target in targets:
            dorkers_proc = self.enumerator_proc(target, gh_token)
            result = dorkers_proc.communicate()[0].decode('utf-8')
            print("[+] Attempted to find subdomains on github for '" + target + "':", result, sep='\n\n')
            self.output_buffer += result
        # clean up duplicates and non-valid domain formats from output before storing results
        self.results_set = set(subdom for subdom in set_of_lines_from_text(self.output_buffer) if is_valid_domain_format(subdom))
        store_results(text_from_set_of_lines(self.results_set), self.output_file)
        print("[+] Dorking GitHub for subdomains completed")
