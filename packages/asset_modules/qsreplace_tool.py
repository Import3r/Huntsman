#! /usr/bin/python3

from shutil import which
from packages.static_paths import ENDP_ALL_RAW_FILE, INST_TOOLS_DIR
from packages.install_handler import update_install_path
from packages.common_utils import store_results, set_of_lines_from_text, text_from_set_of_lines
from os import chmod, path, makedirs, rename
from subprocess import Popen, run, PIPE, STDOUT


class QSReplace:
    asset_name = "qsreplace"
    remote_repo_name = "qsreplace"
    remote_repo_url = "github.com/tomnomnom/qsreplace"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)
        self.output_buffer = ""
        self.results_set = set()
    

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
            update_install_path(self, final_path)
        else:
            print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
            exit()


    def filter_proc(self):
        return Popen(f"{self.asset_path} -a", shell=True, stdin=PIPE, stdout=PIPE)


    def thread_handler(self, endpoints):
        print("[+] Removing duplicates from collected endpoints...")
        qsreplace_proc = self.filter_proc()
        qsreplace_stdin = text_from_set_of_lines(endpoints).encode('utf-8')
        self.output_buffer = qsreplace_proc.communicate(input=qsreplace_stdin)[0].decode("utf-8")
        self.results_set = set(url.rstrip('/') for url in set_of_lines_from_text(self.output_buffer))
        store_results(text_from_set_of_lines(self.results_set), ENDP_ALL_RAW_FILE)
        print("[+] Removing duplicate endpoints completed")
