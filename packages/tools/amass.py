#! /usr/bin/python3

from packages.package_imports import *
from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR

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
        return run_async(f"{self.exec_path} enum --passive -d {target_domains} -nolocaldb", shell=True, stdout=PIPE, stderr=DEVNULL)
