#! /usr/bin/python3

from sys import executable, argv as arg
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

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""

with open(path.join(getcwd(), 'tools.json'), 'r') as json_file:
    tools = json.load(json_file)


def update_json_file():
    with open(path.join(getcwd(), 'tools.json'), 'w') as json_file:
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


def check_reachable(target):
        try:
            requests.head("http://" + target.split('http://')[-1])  # Change this to a more reliable method
        except:
            print("Problem with reaching target: '" + target + "'")
            exit()


def valid_github_token(github_token):
    return requests.get('https://api.github.com/user', headers={'authorization': 'Bearer ' + github_token}).ok


def verify_args(target_arg, github_token):
    if not valid_github_token(github_token):
        print("Faulty Github token, please provide a valid one")
        exit()

    for target in target_arg.split(','):
        check_reachable(target)


def enum_subdoms(target_arg, token, blacklist_arg):
    # fire up amass, github subdomain enumerator
    print("Running 'Amass' script...")
    time.sleep(1)
    amass_proc = run_async([tools['amass']["path"], "enum", "-d", target_arg])
    print("Running 'github-subdomains' script...")
    time.sleep(1)
    github_procs = [(taget, run_async([tools['github-subdomains']["path"], '-t', token, '-d', target], stdout=PIPE))
                    for target in target_arg.split(',')]
    github_subdoms = ''
    time.sleep(2)
    print("\nWaiting for initial sequence to conclude, please wait...")
    for target, proc in github_procs:
        proc.wait()
        proc_output = proc.communicate()[0].decode('utf-8').lstrip('\n')
        print("\nFound subdomains on github for the target: " + target)
        github_subdoms += proc_output
    amass_proc.wait()
    amass_subdoms = run([tools['amass']["path"], 'db', '-d', target_arg,
                        '--names'], capture_output=True).stdout.decode('utf-8')

    # write individual subdomain enum results to files
    print("Writing initial results to files...")
    time.sleep(1)
    with open(path.join(BASE_DIR, SUB_GIT_FILE), 'w') as f:
        f.write(github_subdoms)
    with open(path.join(BASE_DIR, SUB_AMASS_FILE), 'w') as f:
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
            response = requests.head("http://" + subdomain, allow_redirects=True)
            valid_subdoms_set.add(subdomain)
            unique_dest_set.add(re.fullmatch('[A-Za-z]+:\/\/([A-Za-z0-9\-\.]+).*', response.url)[1])
            print('[+] resolved: ' + subdomain)
        except:
            print('[-] removed: ' + subdomain)
        time.sleep(1)

    # write all resolvable subdomains to file
    print("\nWriting cleaned results to files...")
    time.sleep(1)
    with open(path.join(BASE_DIR, RESOLV_SUB_FILE), 'w') as f:
        f.write('\n'.join(valid_subdoms_set) + '\n')
    # write all subdomains with unique destinations to file
    with open(path.join(BASE_DIR, UNIQUE_SUB_FILE), 'w') as f:
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
    aquatone_proc = run_async([tools['aquatone']["path"], "-scan-timeout", "500", "-threads", "1", "-out", path.join(BASE_DIR, AQUATONE_RES_DIR)], stdin=open(path.join(BASE_DIR, UNIQUE_SUB_FILE), 'r'), stdout=open(devnull, 'w'))

    # Use collected subdomains with subdomainizer
    print("\n\nFIRING 'SUBDOMAINIZER' TO HUNT STORED SECRETS...")
    time.sleep(1)
    mkdir(path.join(BASE_DIR, SBDZ_RES_DIR))
    SUBDOMS_F = path.join(BASE_DIR, SBDZ_RES_DIR, SBDZ_SUB_FILE)
    SECRETS_F = path.join(BASE_DIR, SBDZ_RES_DIR, SBDZ_SECRET_FILE)
    CLOUD_F = path.join(BASE_DIR, SBDZ_RES_DIR, SBDZ_CLOUD_FILE)
    subdomainizer_proc = run_async([tools['subdomainizer']["path"], "-l", path.join(BASE_DIR, UNIQUE_SUB_FILE),
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
    verify_args(target_arg, github_token)

    check_for_tools()

    # checking for previous runs of 'Huntsman'
    if path.isdir(BASE_DIR):
        print('results directory exists. exiting to avoid loss of previous reports...')
        exit()
    else:
        mkdir(BASE_DIR)

    start_routine(target_arg, github_token, blacklist_arg)

    # notify end of routine and exit
    print("\nOperation successful. All results are stored at '" + BASE_DIR + "'.")
    print("Shutting down...")
    time.sleep(2)


# calling main function with KeyboardInterrupt handling
try:
    setpgrp()
    main()
except KeyboardInterrupt:
    print("\n\nExiting...")
    killpg(0, signal.SIGKILL)
