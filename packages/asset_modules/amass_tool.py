#! /usr/bin/python3

from shutil import which
import subprocess
from packages.static_paths import SUB_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.common_utils import store_results
from os import chmod, path, makedirs
from subprocess import Popen, PIPE
import zipfile, wget


class Amass:
    asset_name = "amass"
    output_file_name = "subdomains.amass"
    remote_repo_name = "Amass"
    zipfile_name = "amass.zip"
    compiled_zip_url = "https://github.com/OWASP/Amass/releases/download/v3.13.4/amass_linux_amd64.zip"


    def __init__(self, operation, subdom_results_dir) -> None:
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.output_file = path.join(subdom_results_dir, self.output_file_name)
        self.install_path = path.join(operation.inst_tools_dir, self.remote_repo_name)


    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):
        makedirs(self.install_path, exist_ok=True)
        zip_path = path.join(self.install_path, self.zipfile_name)
        if not path.exists(zip_path):
            wget.download(self.compiled_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            relative_path = ''.join([x for x in zip_file.namelist() if path.basename(x) == self.asset_name])
            zip_file.extractall(self.install_path)
        
        if path.exists(self.install_path):
            self.update_install_path(path.join(self.install_path, relative_path))
        else:
            print("[X] Failed to properly decompress '" + self.zipfile_name + "'\nexiting...")
            exit()


    def enumerator_proc(self, domains):
        return Popen(f"{self.asset_path} enum --passive -d {domains} -nolocaldb", shell=True, stdout=PIPE)


    def thread_handler(self, domains):
        print("[+] Firing 'Amass' to hunt subdomains...")
        target_domains = ','.join(domains)
        amass_proc = self.enumerator_proc(target_domains)
        output_buffer = amass_proc.communicate()[0].decode("utf-8")
        store_results(output_buffer, self.output_file)
        print("[+] Amass retrieved the following subdomains:", output_buffer, sep='\n\n')
        print("[+] Amass hunt completed")
        print("[+] 'HUNTSMAN' sequence in progress...\n\n")
