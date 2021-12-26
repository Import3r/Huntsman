#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from packages.common_utils import store_results, lines_data_from_set, update_install_path
from os import path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT, DEVNULL


class GoSpider:
    exec_name = "gospider"
    results_dir_name = "gospider_results"
    input_file_name = "subdom-urls.temp"
    remote_repo_name = "gospider"
    remote_repo_url = "github.com/jaeles-project/gospider"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)
        self.input_file = path.join(self.output_dir, self.input_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def crawler_proc(self, subdomains):
        makedirs(self.output_dir, exist_ok = True)  # ensure output dir exist to avoid failure of the subprocess
        base_endpoints = set("http://" + subdom for subdom in subdomains)
        store_results(lines_data_from_set(base_endpoints), self.input_file)
        return Popen(f"{self.exec_path} -S {self.input_file} --other-source -t 20 -o {self.output_dir} -d 6 -q | grep -E -o '[a-zA-Z]+://[^\ ]+'", shell=True, stdout=PIPE, stderr=DEVNULL)


    def install(self):
        binary_path = path.join(path.expanduser("~"),"go","bin",self.exec_name)
        makedirs(self.install_path, exist_ok=True)
        run(f"GO111MODULE=on go get -u {self.remote_repo_url}", shell=True, stderr=STDOUT)

        if path.exists(binary_path):
            final_path = path.join(self.install_path, self.exec_name)
            rename(binary_path, final_path)
            update_install_path(self, final_path)
        else:
            print("[X] Failed to install '" + self.exec_name + "'\nexiting...")
            exit()