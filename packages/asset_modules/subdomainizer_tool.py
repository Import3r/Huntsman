#! /usr/bin/python3

from shutil import which
from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from os import chmod, path, makedirs
from sys import executable
from subprocess import Popen, run, STDOUT, DEVNULL
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


    def __init__(self, operation) -> None:
        self.inst_tools_dir = operation.inst_tools_dir
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.output_dir = path.join(operation.res_root_dir, self.results_dir_name)
        self.subs_loot_file = path.join(operation.res_root_dir, self.results_dir_name, self.subs_file_name)
        self.secret_loot_file = path.join(operation.res_root_dir, self.results_dir_name, self.secrets_file_name) 
        self.cloud_loot_file = path.join(operation.res_root_dir, self.results_dir_name, self.cloud_file_name)
        self.install_path = path.join(operation.inst_tools_dir, self.remote_repo_name)
        self.req_file = path.join(self.install_path, self.req_file_name)

    
    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):
        if not path.exists(self.install_path):
            git.cmd.Git(self.inst_tools_dir).clone(self.remote_repo_url)
        run([executable, "-m", "pip", "install", "-r", self.req_file], stderr=STDOUT)
        
        if path.exists(path.join(self.install_path, self.asset_name)):
            self.update_install_path(path.join(self.install_path, self.asset_name))
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def scraper_proc(self, subdoms_file):
        return Popen(f"{self.asset_path} -k -l {subdoms_file} -o {self.subs_loot_file} -sop {self.secret_loot_file} -cop {self.cloud_loot_file}", shell=True, stdout=DEVNULL)
    

    def thread_handler(self, subdoms_file):
        print("[+] Firing 'Subdomainizer' to hunt stored secrets...")
        makedirs(self.output_dir, exist_ok = True)  # ensure output dir exist to avoid failure of the subprocess 
        subdomainizer_proc = self.scraper_proc(subdoms_file)
        subdomainizer_proc.wait()
        print("[+] Subdomainizer hunt completed")
