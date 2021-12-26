#! /usr/bin/python3

from packages.static_paths import HM_WORDLISTS_DIR, RES_ROOT_DIR
from packages.common_utils import update_install_path
from os import path
from sys import executable
from subprocess import run, STDOUT


class Altdns:
    exec_name = "altdns"
    output_file_name = "subdom-permutations.altdns"
    permutations_list_name = "altdns-subdom-keywords.txt"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.output_file = path.join(RES_ROOT_DIR, self.output_file_name)
        self.permutations_list = path.join(HM_WORDLISTS_DIR, self.permutations_list_name)


    def subdomains_perms(self, subdoms_file):
        return run(f"{self.exec_path} -i {subdoms_file} -o {self.output_file_name} -w {self.permutations_list}", shell=True, capture_output=True).stdout.decode('utf-8')


    def install(self):
        run([executable, "-m", "pip", "install", "py-altdns==1.0.2"], stderr=STDOUT)
        update_install_path(self, path.join(self.install_path, self.exec_name))