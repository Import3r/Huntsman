#! /usr/bin/python3

from packages.static_paths import INST_TOOLS_DIR
from packages.install_handler import update_install_path
import packages.asset_loader
from os import path, makedirs
from subprocess import run, PIPE, DEVNULL
import zipfile, wget


class MassDNS:
    asset_name = "massdns"
    remote_repo_name = "massdns"
    zipfile_name = "massdns.zip"
    compiled_zip_url = "https://github.com/blechschmidt/massdns/archive/refs/tags/v1.0.0.zip"
    dns_resolvers_list = ""

    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def subdom_resolver_proc(self, domains_file):
        self.dns_resolvers_list = packages.asset_loader.loaded_assets["dns_resolvers_ip_list"].asset_path
        return run(f"{self.asset_path} -r {self.dns_resolvers_list} -t AAAA {domains_file} -o S | grep -oE '^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+' | sort -u", shell=True, stdout=PIPE, stderr=DEVNULL)


    def install(self):       
        makedirs(self.install_path, exist_ok=True)
        zip_path = path.join(self.install_path, self.zipfile_name)
        if not path.exists(zip_path):
            wget.download(self.compiled_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(self.install_path)
            zip_root_dir_name = zip_file.namelist()[0]
            unzipped_dir = path.join(self.install_path, zip_root_dir_name)
        
        if path.exists(unzipped_dir):
            run(f"make -C {unzipped_dir}", shell=True)
            update_install_path(self, path.join(unzipped_dir, 'bin', self.asset_name))
        else:
            print("[X] Failed to properly decompress '" + self.zipfile_name + "'\nexiting...")
            exit()