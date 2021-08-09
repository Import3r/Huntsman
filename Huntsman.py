#! /usr/bin/python3

import tools_path
from sys import argv as arg
from subprocess import run, PIPE
from subprocess import Popen as run_async
from shutil import which
import os
import requests
import re
import time
import signal

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""
BASE_DIR = 'huntsman_results/'
UNIQUE_SUB_FILE = 'unique-subdomains.all'
RESOLV_SUB_FILE = 'resolvable-subdomains.all'
SUB_GIT_FILE = 'subdomains.github'
SUB_AMASS_FILE = 'subdomains.amass'
AQUATONE_RES_DIR = 'aquatone_results/'
SBDZ_RES_DIR = 'subdomainizer_results/'
SBDZ_SECRET_FILE = 'secrets.subdomainizer'
SBDZ_SUB_FILE = 'subdomains.subdomainizer'
SBDZ_CLOUD_FILE = 'cloud-services.subdomainizer'
tools = {'amass': tools_path.amass, 'SubDomainizer.py': tools_path.subdomainizer,
         'github-subdomains.py': tools_path.githubSubEnum, 'aquatone': tools_path.aquatone}


def does_exist(tool):
    return which(tool) is not None or os.path.exists(tool)


def verify_ready(target_arg, github_token):
    missing_tools = []
    for tool in tools.keys():
        if does_exist(tool):
            tools[tool] = tool
        elif not does_exist(tools[tool]):
            missing_tools.append(tool)

    if len(missing_tools):
        for t in missing_tools:
            print("missing tool: '" + t + "'")
        exit()

    if not requests.get('https://api.github.com/user', headers={'authorization': 'Bearer ' + github_token}).ok:
        print("Faulty Github token, please provide a valid one")
        exit()

    for target in target_arg.split(','):
        try:
            requests.head("http://" + target.lstrip('http://'))
        except:
            print("Problem with reaching target: '" + target + "'")
            exit()


def enum_subdoms(target_arg, token, blacklist_arg):
    # fire up amass, github subdomain enumerator
    print("Running 'Amass' script...")
    time.sleep(1)
    amass_proc = run_async([tools['amass'], "enum", "-d", target_arg])
    print("Running 'github-subdomains' script...")
    time.sleep(1)
    github_procs = [run_async([tools['github-subdomains.py'], '-t', token, '-d', target], stdout=PIPE)
                    for target in target_arg.split(',')]
    github_subdoms = ''
    time.sleep(2)
    print("\nWaiting for initial sequence to conclude, please wait...")
    for proc in github_procs:
        proc.wait()
        github_subdoms += proc.communicate()[0].decode('utf-8').lstrip('\n')
    amass_proc.wait()
    amass_subdoms = run([tools['amass'], 'db', '-d', target_arg,
                        '--names'], capture_output=True).stdout.decode('utf-8')

    # write individual subdomain enum results to files
    print("Writing initial results to files...")
    time.sleep(1)
    with open(BASE_DIR + SUB_GIT_FILE, 'w') as f:
        f.write(github_subdoms)
    with open(BASE_DIR + SUB_AMASS_FILE, 'w') as f:
        f.write(amass_subdoms)

    # clean non valid-subdomain formats
    print("Narrowing down results...")
    time.sleep(1)
    total_subdoms_set = set([element for element in (amass_subdoms + github_subdoms).split(
        '\n') if re.fullmatch('^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+$', element) != None])

    # remove blacklisted assets
    blacklist_set = set(blacklist_arg.split(','))
    total_subdoms_set.difference_update(blacklist_set)

    # narrow down results to valid subdomains with unique destinations
    unique_dest_set = set()
    valid_subdoms_set = set()
    for subdomain in total_subdoms_set:
        try:
            response = requests.head(
                "http://" + subdomain, allow_redirects=True)
            valid_subdoms_set.add(subdomain)
            unique_dest_set.add(response.url.split(
                ':')[1].strip('/').split('/')[0])
            print('[+] resolved: ' + subdomain)
        except:
            print('[-] removed: ' + subdomain)
        time.sleep(1)

    # write all resolvable subdomains to file
    print("\nWriting cleaned results to files...")
    time.sleep(1)
    with open(BASE_DIR + RESOLV_SUB_FILE, 'w') as f:
        f.write('\n'.join(valid_subdoms_set) + '\n')
    # write all subdomains with unique destinations to file
    with open(BASE_DIR + UNIQUE_SUB_FILE, 'w') as f:
        f.write('\n'.join(unique_dest_set) + '\n')

    return unique_dest_set


def start_routine(target_arg, github_token, blacklist_arg):
    # Collect subdomains list with unique destinations
    print("\n\nINIATING THE 'HUNTSMAN' SEQUENCE...")
    unique_subdomains = enum_subdoms(target_arg, github_token, blacklist_arg)
    print("\n\nHUNTING SUBDOMAINS => COMPLETE")
    time.sleep(2)

    # Use collected subdomains with aquatone
    print("\n\nFIRING 'AQUATONE' TO SCREENSHOT WEB APPS...")
    time.sleep(1)
    aquatone_proc = run_async([tools['aquatone'], "-scan-timeout", "500", "-threads", "1", "-out", BASE_DIR +
                              AQUATONE_RES_DIR], stdin=open(BASE_DIR + UNIQUE_SUB_FILE, 'r'), stdout=open(os.devnull, 'w'))

    # Use collected subdomains with subdomainizer
    print("\n\nFIRING 'SUBDOMAINIZER' TO HUNT STORED SECRETS...")
    time.sleep(1)
    os.mkdir(BASE_DIR + SBDZ_RES_DIR)
    SUBDOMS_F = BASE_DIR + SBDZ_RES_DIR + SBDZ_SUB_FILE
    SECRETS_F = BASE_DIR + SBDZ_RES_DIR + SBDZ_SECRET_FILE
    CLOUD_F = BASE_DIR + SBDZ_RES_DIR + SBDZ_CLOUD_FILE
    subdomainizer_proc = run_async([tools['SubDomainizer.py'], "-l", BASE_DIR + UNIQUE_SUB_FILE,
                                   "-o", SUBDOMS_F, "-sop", SECRETS_F, "-cop", CLOUD_F, "-k", "-g", "-gt", github_token])

    aquatone_proc.wait()
    subdomainizer_proc.wait()
    print("\n\n'HUNTSMAN' SEQUENCE => COMPLETE")
    time.sleep(1)


def main():
    print(banner)
    try:
        target_arg = arg[1]
        github_token = arg[2]
        try:
            blacklist_arg = arg[3]
        except:
            blacklist_arg = ''
    except:
        print('usage: ' + arg[0] + ' TARGET_DOMAINS' +
              ' GITHUB_TOKEN' + ' [DOMAIN_BLACKLIST]')
        print('\nNote: comma separate multi-inputs')
        exit()

    # validating provided inputs
    verify_ready(target_arg, github_token)

    # checking for previous runs of 'Huntsman'
    if os.path.isdir(BASE_DIR):
        print('results directory exists. exiting to avoid loss of previous reports...')
        exit()
    else:
        os.mkdir(BASE_DIR)

    start_routine(target_arg, github_token, blacklist_arg)

    # notify end of routine and exit
    print("\nOperation successful. All results are stored at '" + BASE_DIR + "'.")
    print("Shutting down...")
    time.sleep(2)


# calling main function with KeyboardInterrupt handling
try:
    os.setpgrp()
    main()
except KeyboardInterrupt:
    print("\n\nExiting...")
    os.killpg(0, signal.SIGKILL)
