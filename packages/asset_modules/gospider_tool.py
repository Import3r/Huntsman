#! /usr/bin/python3

from shutil import which
import threading
from packages.common_utils import store_results
from os import chmod, path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT


class GoSpider:
    asset_name = "gospider"
    results_dir_name = "gospider_results"
    output_file_name = "endpoints.gospider"
    remote_repo_name = "gospider"
    remote_repo_url = "github.com/jaeles-project/gospider"


    def __init__(self, operation, HM) -> None:
        self.ep_results_dir = HM.ep_results_dir
        self.input_file = HM.base_live_ep_file
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.output_dir = path.join(self.ep_results_dir, self.results_dir_name)
        self.output_file = path.join(self.ep_results_dir, self.output_file_name)
        self.install_path = path.join(operation.inst_tools_dir, self.remote_repo_name)


    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):
        binary_path = path.join(path.expanduser("~"),"go","bin",self.asset_name)
        makedirs(self.install_path, exist_ok=True)
        run(f"GO111MODULE=on go get -u {self.remote_repo_url}", shell=True, stderr=STDOUT)

        if path.exists(binary_path):
            final_path = path.join(self.install_path, self.asset_name)
            rename(binary_path, final_path)
            self.update_install_path(final_path)
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def crawler_proc(self):
        return Popen(f"{self.asset_path} -S {self.input_file} -o {self.output_dir} -m 4 -t 20 -c 20 -d 3 -q | grep -E -o '[a-zA-Z]+://[^\ ]+'", shell=True, stdout=PIPE)


    def thread_handler(self):
        print("[+] Firing 'GoSpider' to hunt endpoints...")
        makedirs(self.output_dir, exist_ok = True)  # ensure output dir exist to avoid failure of the subprocess
        gospider_proc = self.crawler_proc()
        output_buffer = gospider_proc.communicate()[0].decode("utf-8")
        store_results(output_buffer, self.output_file)
        print("[+] GoSpider retrieved the following endpoints:", output_buffer, sep='\n\n')
        print("[+] GoSpider hunt completed")
        print("[+] 'HUNTSMAN' sequence in progress...\n\n")


    def activate(self):
        hound_thread = threading.Thread(target=self.thread_handler)
        hound_thread.start()
        return hound_thread