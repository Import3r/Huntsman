#! /usr/bin/python3

from packages.static_paths import ENDP_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from os import path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT


class Waybackurls:
    asset_name = "waybackurls"
    output_file_name = "endpoints.waybackurls"
    remote_repo_name = "waybackurls"
    remote_repo_url = "github.com/tomnomnom/waybackurls"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_file = path.join(ENDP_HOUND_RES_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)

    
    def install(self):
        binary_path = path.join(path.expanduser("~"),"go","bin",self.asset_name)
        makedirs(self.install_path, exist_ok=True)
        run(f"GO111MODULE=on go get -u {self.remote_repo_url}", shell=True, stderr=STDOUT)

        if path.exists(binary_path):
            final_path = path.join(self.install_path, self.asset_name)
            rename(binary_path, final_path)
            update_install_path(self, final_path)
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def enumerator_proc(self, subdoms_file):
        return Popen(f"{self.asset_path} | tee {self.output_file}", shell=True, stdin=open(subdoms_file, 'r'), stdout=PIPE)


    def thread_handler(self, subdoms_file):
        wayback_proc = self.enumerator_proc(subdoms_file)
        wayback_output = wayback_proc.communicate()[0].decode("utf-8")
        return wayback_output