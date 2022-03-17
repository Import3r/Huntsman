#! /usr/bin/python3

from shutil import which
from packages.common_utils import store_results
from os import chmod, path, makedirs, rename
from subprocess import PIPE, Popen, run, STDOUT


class AssetFinder:
    asset_name = "assetfinder"
    output_file_name = "subdomains.assetfinder"
    remote_repo_name = "assetfinder"
    remote_repo_url = "github.com/tomnomnom/assetfinder"


    def __init__(self, operation, subdom_results_dir) -> None:
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.output_file = path.join(subdom_results_dir, self.output_file_name)
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


    def enumerator_proc(self, target):
        return Popen(f"{self.asset_path} -subs-only {target}", shell=True, stdout=PIPE)


    def thread_handler(self, targets):
        print("[+] Firing 'Assetfinder' to hunt subdomains...")
        output_buffer = ""
        for target in targets:
            assetf_proc = self.enumerator_proc(target)
            result = assetf_proc.communicate()[0].decode('utf-8')
            print("[+] Assetfinder found the following subdomains for '" + target + "':", result, sep='\n\n')
            output_buffer += result.rstrip() + "\n"
        store_results(output_buffer, self.output_file)
        print("[+] Assetfinder hunt completed")
        print("[+] 'HUNTSMAN' sequence in progress...\n\n")

