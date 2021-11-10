#! /usr/bin/python3

from packages.package_imports import *
from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR

class GithubDorkers:
    install_type = "from_repo"
    exec_name = "github-subdomains.py"
    req_file_name = "requirements3.txt"
    output_file_name = "subdomains.github"
    remote_repo_name = "github-search"
    remote_repo_url = "https://github.com/gwen001/github-search.git"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_file = path.join(RES_ROOT_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def subdomains(self, target, gh_token):
        return run(f"{self.exec_path} -t {gh_token} -d {target}", shell=True, capture_output=True).stdout.decode('utf-8')
