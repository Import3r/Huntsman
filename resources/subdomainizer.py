#! /usr/bin/python3

from resources.packages import *
from resources.static_names import RES_ROOT_DIR

class Subdomainizer:
    install_type = "from_repo"
    exec_name = "SubDomainizer.py"
    req_file_name = "requirements.txt"
    results_dir_name = "subdomainizer_results"
    subs_file_name = "subdomains.subdomainizer"
    secrets_file_name = "secrets.subdomainizer"
    cloud_file_name = "cloud-services.subdomainizer"
    remote_repo_name = "SubDomainizer"
    remote_repo_url = "https://github.com/nsonaniya2010/SubDomainizer.git"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)
        self.subs_loot_file = path.join(RES_ROOT_DIR, self.results_dir_name, self.subs_file_name)
        self.secret_loot_file = path.join(RES_ROOT_DIR, self.results_dir_name, self.secrets_file_name) 
        self.cloud_loot_file = path.join(RES_ROOT_DIR, self.results_dir_name, self.cloud_file_name)


    def scraper_proc(self, subdoms_file):
        makedirs(self.output_dir, exist_ok = True)  # ensure output dir exist to avoid failure of the subprocess 
        return run_async(f"{self.exec_path} -k -l {subdoms_file} -o {self.subs_loot_file} -sop {self.secret_loot_file} -cop {self.cloud_loot_file}", shell=True)
