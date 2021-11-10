#! /usr/bin/python3

from packages.static_paths import RES_ROOT_DIR
from packages.common_utils import verify_github_token, verify_targets_format, check_for_tools
from packages.huntsman_modules import start_sequence
import packages.tools_loader
from os import path, mkdir, setpgrp, killpg 
from sys import argv
import time, signal

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""


def main():
    print(banner)

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
        packages.tools_loader.amass,
        packages.tools_loader.subdomainizer,
        packages.tools_loader.aquatone,
        packages.tools_loader.github_dorkers,
        packages.tools_loader.gospider,
        packages.tools_loader.waybackurls
    ]
    
    check_for_tools(tools)

    print("\n\n[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    start_sequence(targets, github_token, blacklist_targets)
    
    print("\n\n[+] 'HUNTSMAN' sequence completed")
    time.sleep(1)

    print("[+] Operation succeeded. All results are stored at '" + RES_ROOT_DIR + "'.")
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
