#! /usr/bin/python3

from packages.package_imports import *
from packages.static_paths import *
from packages.common_utils import *
from packages.huntsman_modules import *
import packages.tools_loader

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""


def main():
    print(banner)

    # ensure correct usage of tool
    try:
        target_arg = arg[1]
        github_token = arg[2]
        try:
            blacklist_arg = arg[3]
        except:
            blacklist_arg = ''
    except:
        print('[!] usage:')
        print('\n    ' + arg[0] + ' TARGET_DOMAINS' +
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
