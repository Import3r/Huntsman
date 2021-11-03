#! /usr/bin/python3

from resources.packages import *
from resources.static_names import RES_ROOT_DIR

class Aquatone:
    install_type = "compiled"
    exec_name = "aquatone"
    results_dir_name = "aquatone_results"
    remote_repo_name = "aquatone"
    compiled_zip_url = "https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)


    def snapper_proc(self, subdoms_file):
        return run_async(f"{self.exec_path} -scan-timeout 500 -threads 1 -out {self.output_dir}", shell = True, stdin=open(subdoms_file, 'r'), stdout=DEVNULL)
