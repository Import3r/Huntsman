#! /usr/bin/python3

from packages.static_paths import ENDP_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from packages.common_utils import store_results, set_of_lines_from_text, text_from_set_of_lines
from os import path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT


class Waybackurls:
    asset_name = "waybackurls"
    output_file_name = "endpoints.waybackurls"
    remote_repo_name = "waybackurls"
    remote_repo_url = "github.com/tomnomnom/waybackurls"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_file = path.join(ENDP_HOUND_RES_DIR, self.output_file_name)
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


    def enumerator_proc(self, subdoms_file):
        return Popen(f"{self.asset_path}", shell=True, stdin=open(subdoms_file, 'r'), stdout=PIPE)


    def thread_handler(self, subdoms_file):
        print("[+] Firing 'WaybackURLs' to hunt endpoints...")
        wayback_proc = self.enumerator_proc(subdoms_file)
        self.output_buffer = wayback_proc.communicate()[0].decode("utf-8")
        print("[+] WaybackURLs retrieved the following endpoints:", self.output_buffer, sep='\n\n')
        # clean up duplicates from output before storing results
        self.results_set = set(url.rstrip('/') for url in set_of_lines_from_text(self.output_buffer))
        store_results(text_from_set_of_lines(self.results_set), self.output_file)
        print("[+] WaybackURLs hunt completed")
