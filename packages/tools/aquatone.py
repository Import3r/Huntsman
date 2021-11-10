#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from os import path
from subprocess import Popen, DEVNULL


class Aquatone:
    install_type = "compiled"
    exec_name = "aquatone"
    results_dir_name = "aquatone_results"
    remote_repo_name = "aquatone"
    zipfile_name = "aquatone.zip"
    compiled_zip_url = "https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def snapper_proc(self, subdoms_file):
        return Popen(f"{self.exec_path} -scan-timeout 500 -threads 1 -out {self.output_dir}", shell = True, stdin=open(subdoms_file, 'r'), stdout=DEVNULL)
