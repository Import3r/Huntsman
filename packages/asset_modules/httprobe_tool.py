#! /usr/bin/python3

from packages.static_paths import INST_TOOLS_DIR, ENDP_BASE_LIVE_FILE
from packages.install_handler import update_install_path
from packages.common_utils import store_results, set_of_lines_from_text, text_from_set_of_lines
from os import path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT


class HttProbe:
    asset_name = "httprobe"
    remote_repo_name = "httprobe"
    remote_repo_url = "github.com/tomnomnom/httprobe"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
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


    def discovery_proc(self):
        return Popen(f"{self.asset_path} -t 5000 -p http:8000 -p http:8080 -p https:8443", shell=True, stdin=PIPE, stdout=PIPE)


    def thread_handler(self, subdomains):
        print("[+] Firing 'httprobe' to find the live subdomains...")
        httprobe_proc = self.discovery_proc()
        httprobe_stdin = text_from_set_of_lines(subdomains).encode('utf-8')
        self.output_buffer = httprobe_proc.communicate(input=httprobe_stdin)[0].decode("utf-8")
        print("[+] httprobe found the following web services:", self.output_buffer, sep='\n\n')
        # clean up duplicates from output before storing results
        self.results_set = set(url.rstrip('/') for url in set_of_lines_from_text(self.output_buffer))
        store_results(text_from_set_of_lines(self.results_set), ENDP_BASE_LIVE_FILE)
        print("[+] Live web services discovery completed")
