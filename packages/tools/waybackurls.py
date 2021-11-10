#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from os import path
from subprocess import Popen, PIPE, DEVNULL


class Waybackurls:
    install_type = "go_package"
    exec_name = "waybackurls"
    output_file_name = "endpoints.waybackurls"
    remote_repo_name = "waybackurls"
    remote_repo_url = "github.com/tomnomnom/waybackurls"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_file = path.join(RES_ROOT_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def enumerator_proc(self, subdoms_file):
        return Popen(f"{self.exec_path} | tee {self.output_file}", shell=True, stdin=open(subdoms_file, 'r'), stdout=PIPE, stderr=DEVNULL)
