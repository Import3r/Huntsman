#! /usr/bin/python3

from packages.static_paths import SUB_HOUND_RES_DIR, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from packages.common_utils import store_results
from os import path, makedirs, rename
from subprocess import PIPE, Popen, run, STDOUT


class AssetFinder:
    asset_name = "assetfinder"
    output_file_name = "subdomains.assetfinder"
    remote_repo_name = "assetfinder"
    remote_repo_url = "github.com/tomnomnom/assetfinder"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_file = path.join(SUB_HOUND_RES_DIR, self.output_file_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.output_buffer = ""


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


    def enumerator_proc(self, target):
        return Popen(f"{self.asset_path} -subs-only {target}", shell=True, stdout=PIPE)


    def thread_handler(self, targets):
        print("[+] Firing 'Assetfinder' to hunt subdomains...")
        for target in targets:
            assetf_proc = self.enumerator_proc(target)
            result = assetf_proc.communicate()[0].decode('utf-8')
            print("[+] Assetfinder found the following subdomains for '" + target + "':", result, sep='\n\n')
            self.output_buffer += result
        store_results(self.output_buffer, self.output_file)
        print("[+] Assetfinder hunt completed")
