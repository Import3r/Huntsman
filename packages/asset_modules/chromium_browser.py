#! /usr/bin/python3

from packages.static_paths import INST_TOOLS_DIR
from packages.install_handler import asset_available, available_in_apt, install_apt_package
from os import path, makedirs, chmod
import wget


class ChromiumBrowser:
    asset_name = "chromium-browser"
    package_url = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"


    def __init__(self) -> None:
        self.install_path = INST_TOOLS_DIR


    def install(self):
        if available_in_apt("chromium-browser"):
            install_apt_package("chromium-browser")
            if not asset_available("chromium-browser"):
                print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
                exit()
        else:
            makedirs(self.install_path, exist_ok=True)
            deb_pkg_path = path.join(INST_TOOLS_DIR, "google-chrome.deb")
            wget.download(self.package_url, deb_pkg_path)
            install_apt_package(path.abspath(deb_pkg_path))
            if not asset_available("google-chrome"):
                print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
                exit()
