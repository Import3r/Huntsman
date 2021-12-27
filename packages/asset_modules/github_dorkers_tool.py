#! /usr/bin/python3

from packages.static_paths import SUB_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from os import path
from sys import executable
from subprocess import PIPE, Popen, run, STDOUT
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


    def enumerator_proc(self, target, gh_token):
        return Popen(f"{self.asset_path} -t {gh_token} -d {target}", shell=True, stdout=PIPE)


    def install(self):
        if not path.exists(self.install_path):
            git.cmd.Git(INST_TOOLS_DIR).clone(self.remote_repo_url)
        run([executable, "-m", "pip", "install", "-r", self.req_file], stderr=STDOUT)
        
        if path.exists(path.join(self.install_path, self.asset_name)):
            update_install_path(self, path.join(self.install_path, self.asset_name))
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()