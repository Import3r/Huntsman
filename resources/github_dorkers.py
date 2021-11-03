#! /usr/bin/python3

from resources.packages import *
from resources.static_names import RES_ROOT_DIR

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


    def subdomains(self, target, gh_token):
        return run(f"{self.exec_path} -t {gh_token} -d {target}", shell=True, capture_output=True).stdout.decode('utf-8')
