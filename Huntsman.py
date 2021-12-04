#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR, SUB_MASTER_FILE
from packages.common_utils import verify_github_token, verify_targets_format, check_for_tools
import packages.tools_loader as loaded_tools
import packages.huntsman_hounds.subdomain_hunter as subdomain_hound
import packages.huntsman_hounds.endpoint_hunter as endpoint_hound
from os import path, mkdir, setpgrp, killpg 
from sys import argv
import time, signal

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""


def verify_ready():
    # ensure correct usage of tool
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

    # validating provided inputs
    verify_github_token(github_token)
    verify_targets_format(targets)

    # checking for previous runs of 'Huntsman'
    if path.isdir(RES_ROOT_DIR):
        print("[!] Results directory exists. Move or delete '" + RES_ROOT_DIR + "' to initiate.")
        print("[!] Exiting to avoid loss of previous results...")
        exit()
    else:
        mkdir(RES_ROOT_DIR)
    
    tools = [
        loaded_tools.amass,
        loaded_tools.subdomainizer,
        loaded_tools.aquatone,
        loaded_tools.github_dorkers,
        loaded_tools.gospider,
        loaded_tools.waybackurls
    ]
    
    check_for_tools(tools)

    print("\n\n[+] Ready to engage.\n\n")
    time.sleep(1)
    return (targets, blacklist_targets, github_token)


def main():
    print(banner)

    targets, blacklist_targets, github_token = verify_ready()

    print("\n\n[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    all_subdomains = subdomain_hound.activate(targets, github_token, blacklist_targets)

    print("[+] Firing 'Aquatone' to screen web apps...")
    time.sleep(1)
    aquatone = loaded_tools.aquatone
    aquatone_proc = aquatone.snapper_proc(SUB_MASTER_FILE)

    print("[+] Firing 'Subdomainizer' to hunt stored secrets...")
    time.sleep(1)
    subdomainizer = loaded_tools.subdomainizer
    subdomainizer_proc = subdomainizer.scraper_proc(SUB_MASTER_FILE)

    all_endpoints = endpoint_hound.activate(all_subdomains, SUB_MASTER_FILE)

    aquatone_proc.wait()
    subdomainizer_proc.wait()

    print("\n\n[+] 'HUNTSMAN' sequence completed")
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
