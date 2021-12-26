#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from os import path, makedirs
from sys import executable
from subprocess import Popen, run, STDOUT, PIPE
import git


class Subdomainizer:
    asset_name = "SubDomainizer.py"
    req_file_name = "requirements.txt"
    results_dir_name = "subdomainizer_results"
    subs_file_name = "subdomains.subdomainizer"
    secrets_file_name = "secrets.subdomainizer"
    cloud_file_name = "cloud-services.subdomainizer"
    remote_repo_name = "SubDomainizer"
    remote_repo_url = "https://github.com/nsonaniya2010/SubDomainizer.git"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)
        self.subs_loot_file = path.join(RES_ROOT_DIR, self.results_dir_name, self.subs_file_name)
        self.secret_loot_file = path.join(RES_ROOT_DIR, self.results_dir_name, self.secrets_file_name) 
        self.cloud_loot_file = path.join(RES_ROOT_DIR, self.results_dir_name, self.cloud_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.req_file = path.join(self.install_path, self.req_file_name)


    def scraper_proc(self, subdoms_file):
        makedirs(self.output_dir, exist_ok = True)  # ensure output dir exist to avoid failure of the subprocess 
        return Popen(f"{self.asset_path} -k -l {subdoms_file} -o {self.subs_loot_file} -sop {self.secret_loot_file} -cop {self.cloud_loot_file}", shell=True, stdout=PIPE)
    
    
    def install(self):
        if not path.exists(self.install_path):
            git.cmd.Git(INST_TOOLS_DIR).clone(self.remote_repo_url)
        run([executable, "-m", "pip", "install", "-r", self.req_file], stderr=STDOUT)
        
        if path.exists(path.join(self.install_path, self.asset_name)):
            update_install_path(self, path.join(self.install_path, self.asset_name))
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()