#! /usr/bin/python3

from packages.static_paths import INST_TOOLS_DIR, PATHS_JSON_FILE
import packages.json_handler
from os import path, rename, chmod, makedirs, geteuid
from subprocess import run, STDOUT
from sys import executable
from shutil import which
import apt, git, wget, zipfile, re, requests
from sys import executable


def lines_set_from_bytes(data):
    return set(data.decode('utf-8').strip().split('\n'))


def lines_data_from_set(given_set):
    return "\n".join(given_set)


def store_results(data_string, file_path):
    with open(file_path, 'w') as f:
        f.write(data_string)


def update_install_path(tool, new_path):
    full_path = path.abspath(new_path)
    tool.exec_path = full_path
    chmod(full_path, 0o744)
    
    paths = packages.json_handler.read_from(PATHS_JSON_FILE)
    paths[tool.exec_name] = full_path
    packages.json_handler.write_data_to(PATHS_JSON_FILE, paths)


def auto_install(required_tools):
    makedirs(INST_TOOLS_DIR, exist_ok=True)
    for tool in required_tools:
        try:
            tool.install()
        except Exception as e:
            print("[X] The following exception occured when installing '" + tool.exec_name + "':")
            print(e)
            exit()


def available_in_apt(pkg_name):
    return apt.Cache().get(pkg_name) is not None


def tool_exists(tool):
    return which(tool) is not None or path.exists(tool)


def ask_for_path(tool):
    while True:
        path = input("[?] Please enter the full path for '" + tool.exec_name + "': ")
        if tool_exists(path):
            update_install_path(tool, path)
            return
        else:
            print("[!] Invalid path.")


def offer_store_paths(required_tools):
    while True:
        choice = input("[?] Would you like to enter the path for each tool you have manually? (Y)es, (N)o: ")
        if choice.upper() == 'Y':
            for tool in required_tools:
                ask_for_path(tool)   
            print("[+] Paths for tools were saved successfully.")
            return
        elif choice.upper() == 'N':
            print("[!] Install the missing tools manually, or run the script again. Bye!")
            exit()
        else:
            print("[!] Please enter 'Y' or 'N' only.")


def offer_install(required_tools):
    while True:
        choice = input("[?] Would you like me to pull the remaining tools for you? (Y)es, (N)o, (Q)uit: ")
        if choice.upper() == 'Y':
            auto_install(required_tools)
            return
        elif choice.upper() == 'N':
            offer_store_paths(required_tools)
            return
        elif choice.upper() == 'Q':
            print("[!] Install the missing tools manually, or run the script again. Bye!")
            exit()
        else:
            print("[!] Please enter 'Y', 'N', or 'Q' only.")


def install_browser(package):
    install_cmd = ["apt-get", "install", package, "-y"]
    if geteuid() != 0:
        install_cmd = ["sudo"] + install_cmd
    try:
        print("[+] Installing " + package + "...")
        run(install_cmd, stderr=STDOUT)
    except Exception as e:
        print("[X] The following exception occured when installing '" + package + "':")
        print(e)
        exit()


def offer_browser():
    while True:
        choice = input("[?] Missing google-chrome/chromium-browser required by 'aquatone'.\nDo you want to install it now? (Y)es, (N)o: ")
        if choice.upper() == 'Y':
            if available_in_apt("chromium-browser"):
                install_browser("chromium-browser")
                return
            else:
                deb_pkg = path.join(INST_TOOLS_DIR, "google-chrome.deb")
                wget.download("https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", deb_pkg)
                install_browser("./" + deb_pkg)
                return
        elif choice.upper() == 'N':
            print("[!] Install 'google-chrome' or 'chromium-browser' manually, or run the script again. Bye!")
            exit()
        else:
            print("[!] Please enter 'Y' or 'N' only.")


def warn_missing(missing_tools):
    for tool in missing_tools:
        print("[!] missing tool: '" + tool.exec_name + "'")


def check_for_tools(tools):
    if not tool_exists("chromium-browser") and not tool_exists("google-chrome"):
        offer_browser()

    missing_tools = set()
    for tool in tools:
        tool_name = tool.exec_name
        if tool_exists(tool_name):
            tool.exec_path = tool_name
        elif not tool_exists(tool.exec_path):
            missing_tools.add(tool)

    if missing_tools:
        warn_missing(missing_tools)
        offer_install(missing_tools)

    print("\n\n[+] Ready to engage.\n\n")


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


def is_valid_domain_format(string):
    return re.fullmatch('^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+$', string) != None


def verify_github_token(github_token):
    if not valid_github_token(github_token):
        print("[X] Faulty Github token, please provide a valid one")
        exit()


def verify_reachable_targets(targets):
    for target in targets:
        if not reachable(target):
            print("[X] Problem with reaching target: '" + target + "'")
            exit()


def verify_targets_format(targets):
    for target in targets:
            if not is_valid_domain_format(target):
                print("[X] The target: '" + target + "' is not a valid domain format. Make sure to use a valid domain with no schema")
                exit()


def remove_blacklist(blacklist, subdoms_set):
    # remove blacklisted assets
    subdoms_set.difference_update(blacklist)


def resolved_targets(targets):
    # narrow down results to valid subdomains with unique destinations
    unique_dest_set = set()
    for subdomain in targets:
        try:
            response = requests.head("http://" + subdomain, allow_redirects=True)
            unique_dest_set.add(re.fullmatch('[A-Za-z]+:\/\/([A-Za-z0-9\-\.]+).*', response.url)[1])
            print('[+] resolved: ' + subdomain)
        except:
            print('[+] removed: ' + subdomain)
    return unique_dest_set
