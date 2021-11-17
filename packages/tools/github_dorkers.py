#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from packages.common_utils import update_install_path
from os import path
from sys import executable
from subprocess import run, STDOUT
import git


class GithubDorkers:
    exec_name = "github-subdomains.py"
    req_file_name = "requirements3.txt"
    output_file_name = "subdomains.github"
    remote_repo_name = "github-search"
    remote_repo_url = "https://github.com/gwen001/github-search.git"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_file = path.join(RES_ROOT_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.req_file = path.join(self.install_path, self.req_file_name)


    def subdomains(self, target, gh_token):
        return run(f"{self.exec_path} -t {gh_token} -d {target}", shell=True, capture_output=True).stdout.decode('utf-8')


    def install(self):
        if not path.exists(self.install_path):
            git.cmd.Git(INST_TOOLS_DIR).clone(self.remote_repo_url)
        run([executable, "-m", "pip", "install", "-r", self.req_file], stderr=STDOUT)
        update_install_path(self, path.join(self.install_path, self.exec_name))