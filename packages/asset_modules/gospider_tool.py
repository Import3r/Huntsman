#! /usr/bin/python3

from packages.static_paths import ENDP_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.common_utils import store_results, text_from_set_of_lines, set_of_lines_from_text
from packages.install_handler import update_install_path
from os import path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT


class GoSpider:
    asset_name = "gospider"
    results_dir_name = "gospider_results"
    output_file_name = "endpoints.gospider"
    input_file_name = "subdom-urls.temp"
    remote_repo_name = "gospider"
    remote_repo_url = "github.com/jaeles-project/gospider"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_dir = path.join(ENDP_HOUND_RES_DIR, self.results_dir_name)
        self.output_file = path.join(ENDP_HOUND_RES_DIR, self.output_file_name)
        self.input_file = path.join(self.output_dir, self.input_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.output_buffer = ""
        self.results_set = set()


    def install(self):
        binary_path = path.join(path.expanduser("~"),"go","bin",self.asset_name)
        makedirs(self.install_path, exist_ok=True)
        run(f"GO111MODULE=on go get -u {self.remote_repo_url}", shell=True, stderr=STDOUT)

        if path.exists(binary_path):
            final_path = path.join(self.install_path, self.asset_name)
            rename(binary_path, final_path)
            update_install_path(self, final_path)
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def crawler_proc(self):
        return Popen(f"{self.asset_path} -S {self.input_file} -o {self.output_dir} -m 4 -t 20 -c 20 -d 3 -q | grep -E -o '[a-zA-Z]+://[^\ ]+'", shell=True, stdout=PIPE)


    def thread_handler(self, subdomains):
        print("[+] Firing 'GoSpider' to hunt endpoints...")
        makedirs(self.output_dir, exist_ok = True)  # ensure output dir exist to avoid failure of the subprocess
        base_endpoints = set("http://" + subdom for subdom in subdomains)
        store_results(text_from_set_of_lines(base_endpoints), self.input_file)
        gospider_proc = self.crawler_proc()
        self.output_buffer = gospider_proc.communicate()[0].decode("utf-8")
        print("[+] GoSpider retrieved the following endpoints:", self.output_buffer, sep='\n\n')
        # clean up duplicates from output before storing results
        self.results_set = set(url.rstrip('/') for url in set_of_lines_from_text(self.output_buffer))
        store_results(text_from_set_of_lines(self.results_set), self.output_file)
        print("[+] GoSpider hunt completed")