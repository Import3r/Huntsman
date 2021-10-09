#! /usr/bin/python3

from sys import executable, path as here, argv as arg
from subprocess import run, PIPE
from subprocess import STDOUT, Popen as run_async
from shutil import which
from os import path, chmod, makedirs, mkdir, geteuid, getcwd, setpgrp, killpg, devnull
import apt
import git
import wget
import zipfile
import requests
import json
import re
import time
import signal
from default_names import *

SCRIPT_DIR_PATH = path.dirname(arg[0])

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""

with open(path.join(SCRIPT_DIR_PATH, 'tools.json'), 'r') as json_file:
    tools = json.load(json_file)


def update_json_file():
    with open(path.join(SCRIPT_DIR_PATH, 'tools.json'), 'w') as json_file:
        json.dump(tools, json_file, indent=4)


def update_install_path(tool, given_path):
    full_path = path.abspath(given_path)
    tools[tool]["path"] = full_path
    chmod(full_path, 0o744)
    update_json_file()


def install_from_repo(tool):
    url = tools[tool]["install_url"]
    install_path = path.join(TOOLS_DIR, tools[tool]["remote_repo_name"])
    req_name = tools[tool]["req_file_name"]
    file_name = tools[tool]["file_name"]
    
    if not path.exists(install_path):
        git.cmd.Git(TOOLS_DIR).clone(url)
    run([executable, "-m", "pip", "install", "-r", path.join(install_path, req_name)], stderr=STDOUT)
    update_install_path(tool, path.join(install_path, file_name))


def install_compiled(tool):
    url = tools[tool]["install_url"]
    install_path = path.join(TOOLS_DIR, tools[tool]["remote_repo_name"])
    zip_name = tools[tool]["zipfile_name"]
    file_name = tools[tool]["file_name"]

    makedirs(install_path, exist_ok=True)
    wget.download(url, path.join(install_path, zip_name))
    with zipfile.ZipFile(path.join(install_path, zip_name), 'r') as zip_file:
        relative_path = ''.join([x for x in zip_file.namelist() if path.basename(x) == file_name])
        zip_file.extractall(install_path)
    final_path = path.join(install_path, relative_path)
    if path.exists(install_path):
        update_install_path(tool, path.join(install_path, relative_path))
    else:
        print("Failed to properly decompress '" + zip_name + "'\n exiting...")
        exit()


def auto_install(required_tools):
    makedirs(TOOLS_DIR, exist_ok=True)
    for tool in required_tools:
        if tools[tool]["install_type"] == "compiled":
            try:
                install_compiled(tool)
            except Exception as e:
                print("The following exception occured when installing '" + tool + "':")
                print(e)
                exit()
        elif tools[tool]["install_type"] == "from_repo":
            try:
                install_from_repo(tool)
            except Exception as e:
                print("The following exception occured when installing '" + tool + "':")
                print(e)
                exit()


def available_in_apt(pkg_name):
    return apt.Cache().get(pkg_name) is not None


def tool_exists(tool):
    return which(tool) is not None or path.exists(tool)


def ask_for_path(tool):
    while True:
        path = input("Please enter the full path for '" + tool + "': ")
        if tool_exists(path):
            update_install_path(tool, path)
            return
        else:
            print("Invalid path.")


def offer_store_paths(required_tools):
    while True:
        choice = input("Would you like to enter the path for each tool you have manually? (Y)es, (N)o: ")
        if choice.upper() == 'Y':
            for tool in required_tools:
                ask_for_path(tool)   
            print("Paths for tools were saved successfully.")
            return
        elif choice.upper() == 'N':
            print("Install the missing tools manually, or run the script again. Bye!")
            exit()
        else:
            print("Please enter 'Y' or 'N' only.")


def offer_install(required_tools):
    while True:
        choice = input("Would you like me to pull the remaining tools for you? (Y)es, (N)o, (Q)uit: ")
        if choice.upper() == 'Y':
            auto_install(required_tools)
            return
        elif choice.upper() == 'N':
            offer_store_paths(required_tools)
            return
        elif choice.upper() == 'Q':
            print("Install the missing tools manually, or run the script again. Bye!")
            exit()
        else:
            print("Please enter 'Y', 'N', or 'Q' only.")


def install_browser(package):
    install_cmd = ["apt-get", "install", package, "-y"]
    if geteuid() != 0:
        install_cmd = ["sudo"] + install_cmd
    try:
        print("Installing " + package + "...")
        run(install_cmd, stderr=STDOUT)
    except Exception as e:
        print("The following exception occured when installing '" + package + "':")
        print(e)
        exit()


def offer_browser():
    while True:
        choice = input("Missing google-chrome/chromium-browser required by 'aquatone'.\nDo you want to install it now? (Y)es, (N)o: ")
        if choice.upper() == 'Y':
            if available_in_apt("chromium-browser"):
                install_browser("chromium-browser")
                return
            else:
                deb_pkg = path.join(TOOLS_DIR, "google-chrome.deb")
                wget.download("https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", deb_pkg)
                install_browser("./" + deb_pkg)
                return
        elif choice.upper() == 'N':
            print("Install 'google-chrome' or 'chromium-browser' manually, or run the script again. Bye!")
            exit()
        else:
            print("Please enter 'Y' or 'N' only.")


def warn_missing(missing_tools):
    for missing in missing_tools:
        print("missing tool: '" + missing + "'")


def check_for_tools():
    if not tool_exists("chromium-browser") and not tool_exists("google-chrome"):
        offer_browser()

    missing_tools = set()
    for tool in tools.keys():
        if tool_exists(tools[tool]["file_name"]):
            tools[tool]["path"] = tools[tool]["file_name"]
        elif not tool_exists(tools[tool]["path"]):
            missing_tools.add(tool)

    if missing_tools:
        warn_missing(missing_tools)
        offer_install(missing_tools)

    print("\n\nReady to engage.\n\n")


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


def verify_github_token(github_token):
    if not valid_github_token(github_token):
        print("Faulty Github token, please provide a valid one")
        exit()


def verify_reachable_targets(target_arg):
    for target in target_arg.split(','):
        if not reachable(target):
            print("Problem with reaching target: '" + target + "'")
            exit()


def subdomainizer(github_token):
    mkdir(path.join(BASE_DIR, SBDZ_RES_DIR))
    SUBDOMS_FILE = path.join(BASE_DIR, SBDZ_RES_DIR, SBDZ_SUB_FILE)
    SECRETS_FILE = path.join(BASE_DIR, SBDZ_RES_DIR, SBDZ_SECRET_FILE)
    CLOUD_FILE = path.join(BASE_DIR, SBDZ_RES_DIR, SBDZ_CLOUD_FILE)
    return run_async([tools['subdomainizer']["path"], "-l", path.join(BASE_DIR, UNIQUE_SUB_FILE), "-o", SUBDOMS_FILE, "-sop", SECRETS_FILE, "-cop", CLOUD_FILE, "-k", "-g", "-gt", github_token])


def aquatone():
    OUTPUT_DIR = path.join(BASE_DIR, AQUATONE_RES_DIR)
    SUBDOMAINS_FILE = path.join(BASE_DIR, UNIQUE_SUB_FILE)
    return run_async([tools['aquatone']["path"], "-scan-timeout", "500", "-threads", "1", "-out", OUTPUT_DIR], stdin=open(SUBDOMAINS_FILE, 'r'), stdout=open(devnull, 'w'))


def amass(target_arg):
    return run_async([tools['amass']["path"], "enum", "-d", target_arg])


def github_subdomains(target, token):
    return run([tools['github-subdomains']["path"], '-t', token, '-d', target], capture_output=True).stdout.decode('utf-8')


def amass_subdomains(target_arg):
    return run([tools['amass']["path"], 'db', '-d', target_arg, '--names'], capture_output=True).stdout.decode('utf-8')


def subdomains(target_arg, token):
    print("\nFiring 'Amass' to hunt subdomains...")
    time.sleep(1)
    amass_proc = amass(target_arg)

    print("\nHunting subdomains on GitHub...")
    time.sleep(1)
    github_subdoms = ''
    for target in target_arg.split(','):
        print("\nWaiting for Amass...")
        result = github_subdomains(target, token) 
        print("\nAttempted to find subdomains on github for '" + target + "':")
        print(result)
        github_subdoms += result
        time.sleep(1)
    print("\nFinished enumerating github. Waiting for Amass to finish...")
    
    amass_proc.wait()
    print("\nRetrived Amass subdomains:")
    amass_subdoms = amass_subdomains(target_arg)
    print(amass_subdoms)

    # write individual subdomain enum results to files
    print("Writing enumeration results to files...")
    time.sleep(1)
    with open(path.join(BASE_DIR, SUB_GIT_FILE), 'w') as f:
        f.write(github_subdoms)
    with open(path.join(BASE_DIR, SUB_AMASS_FILE), 'w') as f:
        f.write(amass_subdoms)

    return set([element for element in (amass_subdoms + github_subdoms).split('\n') if re.fullmatch('^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+$', element) != None])


def remove_blacklist(blacklist_arg, subdoms_set):
    # remove blacklisted assets
    blacklist_set = set(blacklist_arg.split(','))
    subdoms_set.difference_update(blacklist_set)


def unique_live_targets(targets):
    # narrow down results to valid subdomains with unique destinations
    unique_dest_set = set()
    for subdomain in targets:
        try:
            response = requests.head("http://" + subdomain, allow_redirects=True)
            unique_dest_set.add(re.fullmatch('[A-Za-z]+:\/\/([A-Za-z0-9\-\.]+).*', response.url)[1])
            print('[+] resolved: ' + subdomain)
        except:
            print('[-] removed: ' + subdomain)

    # store results in file
    print("\nWriting resolvable subdomains with unique destinations to files...")
    time.sleep(1)
    with open(path.join(BASE_DIR, UNIQUE_SUB_FILE), 'w') as f:
        f.write('\n'.join(unique_dest_set) + '\n')
        
    return unique_dest_set


def start_sequence(target_arg, github_token, blacklist_arg):
    print("\n\n'HUNTSMAN' SEQUENCE => INITIATE")
    time.sleep(2)

    print("\n\nHUNTING LIVE SUBDOMAINS => INITIATE")
    time.sleep(2)
    # Collect subdomains list with unique destinations
    target_domains = set(target_arg.split(','))
    unique_subdomains = subdomains(target_arg, github_token)
    target_domains.update(unique_subdomains)
    remove_blacklist(blacklist_arg, target_domains)
    live_targets = unique_live_targets(target_domains)
    print("\n\nHUNTING LIVE SUBDOMAINS => COMPLETE")
    time.sleep(2)

    print("\nFiring 'Aquatone' to screen web apps...")
    time.sleep(1)
    aquatone_proc = aquatone()

    print("\nFiring 'Subdomainizer' to hunt stored secrets...")
    time.sleep(1)
    subdomainizer_proc = subdomainizer(github_token)

    aquatone_proc.wait()
    subdomainizer_proc.wait()

    print("\n\n'HUNTSMAN' SEQUENCE => COMPLETE")
    time.sleep(1)


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
        print('usage: ' + arg[0] + ' TARGET_DOMAINS' +
              ' GITHUB_TOKEN' + ' [DOMAIN_BLACKLIST]')
        print('\nNote: comma separate multi-inputs')
        exit()

    # validating provided inputs
    verify_github_token(github_token)
    verify_reachable_targets(target_arg)

    check_for_tools()

    # checking for previous runs of 'Huntsman'
    if path.isdir(BASE_DIR):
        print('Results directory exists. exiting to avoid loss of previous reports...')
        exit()
    else:
        mkdir(BASE_DIR)

    start_sequence(target_arg, github_token, blacklist_arg)

    print("\nOperation successful. All results are stored at '" + BASE_DIR + "'.")
    print("Shutting down...")
    time.sleep(2)


# calling main while handling KeyboardInterrupts
try:
    setpgrp()
    main()
except KeyboardInterrupt:
    print("\n\nExiting...")
    killpg(0, signal.SIGKILL)
