#! /usr/bin/python3

from shutil import which
from packages.install_handler import asset_available
from os import chmod, path
from sys import executable
from subprocess import PIPE, Popen, run, STDOUT


class Altdns:
    asset_name = "altdns"
    output_file_name = "subdom-permutations.altdns"
    permutations_list_name = "altdns-subdom-keywords.txt"


    def __init__(self, operation) -> None:
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.output_file = path.join(operation.res_root_dir, self.output_file_name)
        self.permutations_list = path.join(operation.wordlists_dir, self.permutations_list_name)


    def subdomains_perms(self, subdoms_file):
        return Popen(f"{self.asset_path} -i {subdoms_file} -o {self.output_file_name} -w {self.permutations_list}", shell=True, stdout=PIPE)


    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):
        run([executable, "-m", "pip", "install", "py-altdns==1.0.2"], stderr=STDOUT)
                
        if asset_available(self.asset_name):
            self.update_install_path(self.asset_name)
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()