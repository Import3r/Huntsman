#! /usr/bin/python3

from resources.packages import *
from resources.static_names import RES_ROOT_DIR

class Waybackurls:
    install_type = "go_package"
    exec_name = "waybackurls"
    output_file_name = "endpoints.waybackurls"
    remote_repo_name = "waybackurls"
    remote_repo_url = "github.com/tomnomnom/waybackurls"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_file = path.join(RES_ROOT_DIR, self.output_file_name)


    def enumerator_proc(self, subdoms_file):
        return run_async(f"{self.exec_path} | tee {self.output_file}", shell=True, stdin=open(subdoms_file, 'r'), stdout=PIPE, stderr=DEVNULL)
