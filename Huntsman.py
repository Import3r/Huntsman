#! /usr/bin/python3

from sys import argv as arg
from subprocess import run, PIPE
from subprocess import Popen as run_async
import os, requests, re, time, signal

amass = '/home/sigma/git_repos/public_tools[RANDOM]/Amass/amass_linux_amd64/amass'
subdomainizer = '/home/sigma/git_repos/public_tools[RANDOM]/SubDomainizer/SubDomainizer.py'
githubSubEnum = '/home/sigma/git_repos/public_tools[RANDOM]/github-search/github-subdomains.py'
aquatone = '/home/sigma/git_repos/public_tools[RANDOM]/aquatone/aquatone'
banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""
BASE_DIR = 'huntsman_results/'


def verify_ready(target_arg, github_token):
    if not os.path.isfile(amass):
        print("missing 'amass'")
        exit()
    if not os.path.isfile(subdomainizer):
        print("missing 'subdomainizer'")
        exit()
    if not os.path.isfile(githubSubEnum):
        print("missing 'github Subdomain Enum'")
        exit()
    if not os.path.isfile(aquatone):
        print("missing 'Aquatone'")
        exit()
    if not requests.get('https://api.github.com/user', headers = {'authorization': 'Bearer ' + github_token}).ok:
        print("Faulty Github token, please provide a valid one")
        exit()
    for target in target_arg.split(','):
        try:
            requests.head("http://" + target.lstrip('http://'))
        except:
            print("Problem with provided target: '" + target + "'")
            exit()


def enum_subdoms(target_arg, token):
    # fire up amass, github subdomain enumerator
    print("Running 'Amass' script...")
    time.sleep(1)
    amass_proc = run_async([amass, "enum", "-d", target_arg]) 
    print("Running 'github-subdomains' script...")
    time.sleep(1)
    github_procs = [run_async([githubSubEnum, '-t', token, '-d', target], stdout = PIPE) for target in target_arg.split(',')]
    github_subdoms = ''
    time.sleep(2)
    print("\nWaiting for initial sequence to conclude, please wait...")
    for proc in github_procs:
        proc.wait()
        github_subdoms += proc.communicate()[0].decode('utf-8').lstrip('\n')
    amass_proc.wait()
    amass_subdoms = run([amass, 'db', '-d', target_arg, '--names'], capture_output=True).stdout.decode('utf-8')
    
    # write individual subdomain enum results to files
    print("Writing initial results to files...")
    time.sleep(1)
    with open(BASE_DIR + 'subdomains.github', 'w') as git_file:
        git_file.write(github_subdoms)
    with open(BASE_DIR + 'subdomains.amass', 'w') as amass_file:
        amass_file.write(amass_subdoms)
    
    # clean non valid-subdomain formats
    print("Narrowing down results...")
    time.sleep(1)
    total_subdoms_set = set([element for element in (amass_subdoms + github_subdoms).split('\n') if re.fullmatch('^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+$', element) != None])
    
    # narrow down results to valid subdomains with unique destinations
    unique_dest_set = set()
    valid_subdoms_set = set()
    for subdomain in total_subdoms_set:
        try:
            response = requests.head("http://" + subdomain, allow_redirects=True)
            valid_subdoms_set.add(subdomain)
            unique_dest_set.add(response.url.split(':')[1].strip('/').split('/')[0])
            print('[+] resolved: ' + subdomain)
        except:
            print('[-] removed: ' + subdomain)
        
    # write all resolvable subdomains to file
    print("\nWriting cleaned results to files...")
    time.sleep(1)
    with open(BASE_DIR + 'resolvable-subdomains.all', 'w') as valid_subdoms_file:
        valid_subdoms_file.write('\n'.join(valid_subdoms_set) + '\n')
    # write all subdomains with unique destinations to file
    with open(BASE_DIR + 'unique-subdomains.all', 'w') as unique_subdoms_file:
        unique_subdoms_file.write('\n'.join(unique_dest_set) + '\n')

    return unique_dest_set


def main():
    print(banner)
    # checking for proper usage of tool
    try:
        target_arg = arg[1]
        blacklist_arg = arg[2]
        github_token = arg[3]
    except:
        print('usage: ' + arg[0] + ' <target domain>' + ' <subdomain blacklist>' + ' <github token>')
        print('\nNote: comma separate multi-inputs')
        exit()

    # checking for previous runs of 'Huntsman'
    if os.path.isdir(BASE_DIR):
        print('results directory exists. exiting to avoid loss of previous reports...')
        exit()

    # validating inputs
    verify_ready(target_arg, github_token)

    os.mkdir(BASE_DIR)

    # collect subdomains list with unique destinations
    print("\n\nINIATING THE 'HUNTSMAN' SEQUENCE...")
    unique_subdomains = enum_subdoms(target_arg, github_token)
    print('\n\nHUNTING SUBDOMAINS => COMPLETE')
    time.sleep(2)
    

try:
    os.setpgrp()
    main()
except KeyboardInterrupt:
    print("\n\nExiting...")
    os.killpg(0, signal.SIGKILL)
