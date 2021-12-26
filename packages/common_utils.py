#! /usr/bin/python3

from packages.static_paths import INST_TOOLS_DIR, PATHS_JSON_FILE
import packages.json_handler
from os import path, chmod, makedirs, geteuid
from subprocess import run, STDOUT
from shutil import which
import apt, wget, re, requests


def lines_set_from_bytes(data):
    return set(data.decode('utf-8').strip().split('\n'))


def lines_data_from_set(given_set):
    return "\n".join(given_set)


def store_results(data_string, file_path):
    with open(file_path, 'w') as f:
        f.write(data_string)


def update_install_path(asset, new_path):
    full_path = path.abspath(new_path)
    asset.asset_path = full_path
    chmod(full_path, 0o744)
    
    paths = packages.json_handler.read_from(PATHS_JSON_FILE)
    paths[asset.asset_name] = full_path
    packages.json_handler.write_data_to(PATHS_JSON_FILE, paths)


def auto_install(required_assets):
    makedirs(INST_TOOLS_DIR, exist_ok=True)
    for asset in required_assets:
        try:
            asset.install()
        except Exception as e:
            print("[X] The following exception occured when installing '" + asset.asset_name + "':")
            print(e)
            exit()


def available_in_apt(pkg_name):
    return apt.Cache().get(pkg_name) is not None


def asset_available(asset):
    return which(asset) is not None or path.exists(asset)


def ask_for_path(asset):
    while True:
        path = input("[?] Please enter the full path for '" + asset.asset_name + "': ")
        if asset_available(path):
            update_install_path(asset, path)
            return
        else:
            print("[!] Invalid path.")


def offer_to_store_paths(required_assets):
    while True:
        choice = input("[?] Would you like to enter the path for each asset you have manually? (Y)es, (N)o: ")
        if choice.upper() == 'Y':
            for asset in required_assets:
                ask_for_path(asset)   
            print("[+] Paths for assets were saved successfully.")
            return
        elif choice.upper() == 'N':
            print("[!] Install the missing assets manually, or run the script again. Bye!")
            exit()
        else:
            print("[!] Please enter 'Y' or 'N' only.")


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


def offer_install(required_assets):
    while True:
        choice = input("[?] Would you like me to pull the remaining assets for you? (Y)es, (N)o, (Q)uit: ")
        if choice.upper() == 'Y':
            auto_install(required_assets)
            return
        elif choice.upper() == 'N':
            offer_to_store_paths(required_assets)
            return
        elif choice.upper() == 'Q':
            print("[!] Install the missing assets manually, or run the script again. Bye!")
            exit()
        else:
            print("[!] Please enter 'Y', 'N', or 'Q' only.")


def warn_missing(missing_assets):
    for asset in missing_assets:
        print("[!] missing asset: '" + asset.asset_name + "'")


def check_for_assets(assets):
    missing_assets = set()
    for asset in assets:
        asset_name = asset.asset_name
        if asset_available(asset_name):
            asset.asset_path = asset_name
        elif not asset_available(asset.asset_path):
            missing_assets.add(asset)

    if missing_assets:
        warn_missing(missing_assets)
        offer_install(missing_assets)


def reachable(target):
    url_regex = re.fullmatch('([A-Za-z]+:\/\/)*([A-Za-z0-9\-\.]+).*', target)
    target = url_regex[url_regex.lastindex]
    for method in ['http://', 'https://']:
        try:
            requests.head(method + target)
            return True
        except:
            pass
    return False


def valid_github_token(github_token):
    return requests.get('https://api.github.com/user', headers={'authorization': 'Bearer ' + github_token}).ok


def is_valid_domain_format(string):
    return re.fullmatch('^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+$', string) != None


def verify_github_token(github_token):
    if not valid_github_token(github_token):
        print("[X] Faulty Github token, please provide a valid one")
        exit()


def verify_reachable_targets(targets):
    for target in targets:
        if not reachable(target):
            print("[X] Problem with reaching target: '" + target + "'")
            exit()


def verify_targets_format(targets):
    for target in targets:
            if not is_valid_domain_format(target):
                print("[X] The target: '" + target + "' is not a valid domain format. Make sure to use a valid domain with no schema")
                exit()


def remove_blacklist(blacklist, subdoms_set):
    # remove blacklisted assets
    subdoms_set.difference_update(blacklist)


def resolved_targets(targets):
    # narrow down results to valid subdomains with unique destinations
    unique_dest_set = set()
    for subdomain in targets:
        try:
            response = requests.head("http://" + subdomain, allow_redirects=True)
            unique_dest_set.add(re.fullmatch('[A-Za-z]+:\/\/([A-Za-z0-9\-\.]+).*', response.url)[1])
            print('[+] resolved: ' + subdomain)
        except:
            print('[+] removed: ' + subdomain)
    return unique_dest_set
