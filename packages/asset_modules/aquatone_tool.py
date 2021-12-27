#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, INST_TOOLS_DIR
from packages.install_handler import asset_available, update_install_path
from packages.asset_modules.chromium_browser import ChromiumBrowser
from os import path, makedirs
from subprocess import Popen, DEVNULL
import zipfile, wget


class Aquatone:
    asset_name = "aquatone"
    results_dir_name = "aquatone_results"
    remote_repo_name = "aquatone"
    zipfile_name = "aquatone.zip"
    compiled_zip_url = "https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip"


    def __init__(self, given_path) -> None:
        self.asset_path = given_path
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)
        self.install_path = path.join(INST_TOOLS_DIR, self.remote_repo_name)


    def screener_proc(self, subdoms_file):
        return Popen(f"{self.asset_path} -scan-timeout 500 -threads 1 -out {self.output_dir}", shell = True, stdin=open(subdoms_file, 'r'), stdout=DEVNULL)


    def install(self):
        if not asset_available("chromium-browser") and not asset_available("google-chrome"):
            browser = ChromiumBrowser()
            browser.install()
            
        makedirs(self.install_path, exist_ok=True)
        zip_path = path.join(self.install_path, self.zipfile_name)
        if not path.exists(zip_path):
            wget.download(self.compiled_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            relative_path = ''.join([x for x in zip_file.namelist() if path.basename(x) == self.asset_name])
            zip_file.extractall(self.install_path)
        
        if path.exists(self.install_path):
            update_install_path(self, path.join(self.install_path, relative_path))
        else:
            print("[X] Failed to properly decompress '" + self.zipfile_name + "'\nexiting...")
            exit()