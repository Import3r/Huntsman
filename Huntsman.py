#! /usr/bin/python3

from resources.packages import *
from resources.static_names import *
from resources.utils import *
from resources.modules import *

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
        print('[!] Results directory exists. exiting to avoid loss of previous reports...')
        exit()
    else:
        mkdir(RES_ROOT_DIR)

    tools = [
        Amass(paths["amass"]),
        Subdomainizer(paths["SubDomainizer.py"]),
        Aquatone(paths["aquatone"]),
        GithubDorkers(paths["github-subdomains.py"]),
        GoSpider(paths["gospider"]),
        Waybackurls(paths["waybackurls"])
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
