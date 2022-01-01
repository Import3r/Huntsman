#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, SUB_ALL_RSLVD_FILE
from packages.common_utils import valid_github_token, is_valid_domain_format
from packages.install_handler import check_for_assets
import packages.asset_loader
import packages.hound_modules.subdomain_hunter as subdomain_hound
import packages.hound_modules.endpoint_hunter as endpoint_hound
from os import path, mkdir, setpgrp, killpg 
from sys import argv
import time, signal, threading

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""


def verify_ready():
    # ensure correct usage of huntsman
    try:
        target_arg = argv[1]
        github_token = argv[2]
        try:
            blacklist_arg = argv[3]
        except:
            blacklist_arg = ''
    except:
        print('[!] usage:')
        print('\n    ' + argv[0] + ' TARGET_DOMAINS' +
              ' GITHUB_TOKEN' + ' [DOMAIN_BLACKLIST]')
        print('\n[!] comma separate multi-inputs')
        exit()

    targets = set(target_arg.split(','))
    blacklist_targets = set(blacklist_arg.split(','))

    if not valid_github_token(github_token):
        print("[X] Faulty Github token, please provide a valid one")
        exit()

    for target in targets:
        if not is_valid_domain_format(target):
            print("[X] The target: '" + target + "' is not a valid domain format. Make sure to use a valid domain with no schema")
            exit()

    # checking for previous runs of 'Huntsman'
    if path.isdir(RES_ROOT_DIR):
        print("[!] Results directory exists. Move or delete '" + RES_ROOT_DIR + "' to initiate.")
        print("[!] Exiting to avoid loss of previous results...")
        exit()
    else:
        mkdir(RES_ROOT_DIR)
    
    assets = list(packages.asset_loader.loaded_assets.values())
    
    check_for_assets(assets)

    print("\n\n[+] Ready to engage.\n\n")
    time.sleep(1)
    return (targets, blacklist_targets, github_token)


def main():
    print(banner)

    targets, blacklist_targets, github_token = verify_ready()

    print("[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    all_subdomains = subdomain_hound.activate(targets, github_token, blacklist_targets)

    aquatone = packages.asset_loader.loaded_assets["aquatone"]
    subdomainizer = packages.asset_loader.loaded_assets["subdomainizer"]

    aquatone_thread = threading.Thread(target=aquatone.thread_handler, args=(SUB_ALL_RSLVD_FILE,))
    subdomainizer_thread = threading.Thread(target=subdomainizer.thread_handler, args=(SUB_ALL_RSLVD_FILE,))
    subdom_ops_threads = (aquatone_thread, subdomainizer_thread)

    for t in subdom_ops_threads: t.start()

    all_endpoints = endpoint_hound.activate(all_subdomains, SUB_ALL_RSLVD_FILE)

    for t in subdom_ops_threads: print("[+] 'HUNTSMAN' sequence in progress...\n\n"); t.join()

    print("[+] 'HUNTSMAN' sequence completed")
    time.sleep(2)

    print("[+] Operation succeeded. All results are stored at '" + RES_ROOT_DIR + "'.")
    time.sleep(1)
    print("[+] Shutting down...")
    time.sleep(2)


# calling main while handling KeyboardInterrupts
try:
    setpgrp()
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("\n\n[!] Exiting...")
    killpg(0, signal.SIGKILL)
