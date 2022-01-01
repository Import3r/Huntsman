#! /usr/bin/python3

import subprocess
from packages.static_paths import SUB_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from packages.common_utils import store_results, text_from_set_of_lines, set_of_lines_from_text, is_valid_domain_format
from os import path, makedirs
from subprocess import Popen, PIPE, DEVNULL
import zipfile, wget


class Amass:
    asset_name = "amass"
    output_file_name = "subdomains.amass"
    remote_repo_name = "Amass"
    zipfile_name = "amass.zip"
    compiled_zip_url = "https://github.com/OWASP/Amass/releases/download/v3.13.4/amass_linux_amd64.zip"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_file = path.join(SUB_HOUND_RES_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.output_buffer = ""
        self.results_set = set()


    def install(self):
        makedirs(self.install_path, exist_ok=True)
        zip_path = path.join(self.install_path, self.zipfile_name)
        if not path.exists(zip_path):
            wget.download(self.compiled_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            relative_path = ''.join([x for x in zip_file.namelist() if path.basename(x) == self.asset_name])
            zip_file.extractall(self.install_path)
        
        if path.exists(self.install_path):
            update_install_path(self, path.join(self.install_path, relative_path))
        else:
            print("[X] Failed to properly decompress '" + self.zipfile_name + "'\nexiting...")
            exit()


    def enumerator_proc(self, domains):
        return Popen(f"{self.asset_path} enum --passive -d {domains} -nolocaldb", shell=True, stdout=PIPE)


    def thread_handler(self, domains):
        print("[+] Firing 'Amass' to hunt subdomains...")
        target_domains = ','.join(domains)
        amass_proc = self.enumerator_proc(target_domains)
        self.output_buffer = amass_proc.communicate()[0].decode("utf-8")
        print("[+] Amass retrieved the following subdomains:", self.output_buffer, sep='\n\n')
        # clean up duplicates and non-valid domain formats from output before storing results
        self.results_set = set(subdom for subdom in set_of_lines_from_text(self.output_buffer) if is_valid_domain_format(subdom))
        store_results(text_from_set_of_lines(self.results_set), self.output_file)
        print("[+] Amass hunt completed")
