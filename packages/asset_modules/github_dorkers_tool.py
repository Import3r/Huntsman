#! /usr/bin/python3

from shutil import which
from packages.common_utils import store_results
from os import chmod, path
from sys import executable
from subprocess import Popen, run, STDOUT, PIPE
import git
import threading
import time


class GithubDorkers:
    asset_name = "github-subdomains.py"
    req_file_name = "requirements3.txt"
    output_file_name = "subdomains.github"
    remote_repo_name = "github-search"
    remote_repo_url = "https://github.com/gwen001/github-search.git"


    def __init__(self, operation, subdom_results_dir) -> None:
        self.op = operation
        self.inst_tools_dir = operation.inst_tools_dir
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.output_file = path.join(subdom_results_dir, self.output_file_name)
        self.install_path = path.join(operation.inst_tools_dir, self.remote_repo_name)
        self.req_file = path.join(self.install_path, self.req_file_name)


    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):
        if not path.exists(self.install_path):
            git.cmd.Git(self.inst_tools_dir).clone(self.remote_repo_url)
        run([executable, "-m", "pip", "install", "-r", self.req_file], stderr=STDOUT)
        
        if path.exists(path.join(self.install_path, self.asset_name)):
            self.update_install_path(path.join(self.install_path, self.asset_name))
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def enumerator_proc(self, target, gh_token):
        return Popen(f"{self.asset_path} -t {gh_token} -d {target}", shell=True, stdout=PIPE)


    def thread_handler(self):
        print("[+] Dorking GitHub for subdomains...")
        output_buffer = ""
        for target in self.op.targets:
            dorkers_proc = self.enumerator_proc(target, self.op.github_token)
            result = dorkers_proc.communicate()[0].decode('utf-8')
            print("[+] Attempted to find subdomains on github for '" + target + "':", result, sep='\n\n')
            output_buffer += result.rstrip() + "\n"
            time.sleep(5)
        store_results(output_buffer, self.output_file)
        print("[+] Dorking GitHub for subdomains completed")
        print("[+] 'HUNTSMAN' sequence in progress...\n\n")


    def activate(self):
        hound_thread = threading.Thread(target=self.thread_handler)
        hound_thread.start()
        return hound_thread