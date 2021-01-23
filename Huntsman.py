#! /usr/bin/python3

from sys import argv as arg
from subprocess import run
import os, requests

amass = '/home/sigma/git_repos/public_tools[RANDOM]/Amass/amass_linux_amd64/amass'
subdomainizer = '/home/sigma/git_repos/public_tools[RANDOM]/SubDomainizer/SubDomainizer.py'
githubSubEnum = '/home/sigma/git_repos/public_tools[RANDOM]/github-search/github-subdomains.py'
aquatone = '/home/sigma/git_repos/public_tools[RANDOM]/aquatone/aquatone'
banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""

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
            requests.get("http://" + target.lstrip('http://'))
        except:
            print("Problem with provided target: '" + target + "'")
            exit()


def collect_subdomains(target_arg):
    amass_subdoms = subprocess.run(['/home/sigma/git_repos/public_tools[RANDOM]/Amass/amass_linux_amd64/amass', 'db', '-d', target_arg, '--names'], capture_output=True).stdout.decode('utf-8')
    # open('####', 'w').write(amass_subdoms)  # write amass results to file
    # amass_subdoms.rstrip('\n').split('\n')  # returns amass subdomains in a list


def main():
    print(banner)
    try:
        target_arg = arg[1]
        blacklist_arg = arg[2]
        github_token = arg[3]

    except:
        print('usage: ' + arg[0] + ' <target domain>' + ' <subdomain blacklist>' + ' <github token>')
        print('\nNote: comma separate multi-inputs')
        exit()
    
    verify_ready(target_arg, github_token)
    # subprocess.run([amass, "enum","-d", "www.google.com"])
    
    # print("\nenumerating subdomains...")
    


main()
