#! /usr/bin/python3

from shutil import which
from packages.install_handler import asset_available, available_in_apt, install_apt_package
from os import chmod, path, makedirs
import wget


class ChromiumBrowser:
    asset_name = "chromium-browser"
    package_url = "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"


    def __init__(self, install_path) -> None:
        self.install_path = install_path


    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):
        if available_in_apt("chromium-browser"):
            install_apt_package("chromium-browser")
            if not asset_available("chromium-browser"):
                print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
                exit()
        else:
            makedirs(self.install_path, exist_ok=True)
            deb_pkg_path = path.join(self.install_path, "google-chrome.deb")
            wget.download(self.package_url, deb_pkg_path)
            install_apt_package(path.abspath(deb_pkg_path))
            if not asset_available("google-chrome"):
                print("[X] Failed to install '" + self.asset_name + "'\nexiting...")
                exit()
