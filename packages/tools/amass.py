#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from packages.common_utils import update_install_path
from os import path, makedirs
from subprocess import Popen, PIPE, DEVNULL
import zipfile, wget


class Amass:
    install_type = "compiled"
    exec_name = "amass"
    output_file_name = "subdomains.amass"
    remote_repo_name = "Amass"
    zipfile_name = "amass.zip"
    compiled_zip_url = "https://github.com/OWASP/Amass/releases/download/v3.13.4/amass_linux_amd64.zip"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_file = path.join(RES_ROOT_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def enumerator_proc(self, domains):
        target_domains = ','.join(domains)
        return Popen(f"{self.exec_path} enum --passive -d {target_domains} -nolocaldb", shell=True, stdout=PIPE, stderr=DEVNULL)


    def install(self):
        makedirs(self.install_path, exist_ok=True)
        zip_path = path.join(self.install_path, self.zipfile_name)
        if not path.exists(zip_path):
            wget.download(self.compiled_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            relative_path = ''.join([x for x in zip_file.namelist() if path.basename(x) == self.exec_name])
            zip_file.extractall(self.install_path)
        
        if path.exists(self.install_path):
            update_install_path(self, path.join(self.install_path, relative_path))
        else:
            print("[X] Failed to properly decompress '" + self.zipfile_name + "'\nexiting...")
            exit()