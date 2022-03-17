#! /usr/bin/python3

from os import path, geteuid
from subprocess import run, STDOUT
from shutil import which
import apt


def available_in_apt(pkg_name):
    return apt.Cache().get(pkg_name) is not None


def asset_available(asset):
    return which(asset) is not None or path.exists(asset)


def install_apt_package(package):
    install_cmd = ["apt-get", "install", package, "-y"]
    if geteuid() != 0:
        install_cmd = ["sudo"] + install_cmd
    try:
        print("[+] Installing " + package + "...")
        run(install_cmd, stderr=STDOUT)
    except Exception as e:
        print("[X] The following exception occured when installing '" + package + "':")
        print(e)
        exit()


def get_valid_path(asset):
    while True:
        path = input("[?] Please enter the full path for '" + asset.asset_name + "': ")
        if not asset_available(path):
            print("[!] Invalid path.")
        else:
            return path


def prompt_decision(prompt_message, choices):
    while True:
        choice = input(prompt_message).upper()
        if choice not in choices:
            print("[!] Please choose an option from [ " + " / ".join(choices) +" ] only.")
        else: return choice
