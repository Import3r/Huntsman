#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from packages.common_utils import store_results, lines_data_from_set, update_install_path
from os import path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT, DEVNULL


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
    
    
    def install(self):
        binary_path = path.join(path.expanduser("~"),"go","bin",self.exec_name)
        makedirs(self.install_path, exist_ok=True)
        run(f"GO111MODULE=on go get -u {self.remote_repo_url}", shell=True, stderr=STDOUT)

        if path.exists(binary_path):
            final_path = path.join(self.install_path, self.exec_name)
            rename(binary_path, final_path)
            update_install_path(self, final_path)
        else:
            print("[X] Failed to install '" + self.exec_name + "'\nexiting...")
            exit()