#! /usr/bin/python3

from resources.packages import *
from resources.static_names import *
from resources.wrapper_functions import *

SCRIPT_DIR_PATH = path.dirname(arg[0])

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""

with open(path.join(SCRIPT_DIR_PATH, HM_PKGS_DIR ,JSON_FILE), 'r') as json_file:
    tools = json.load(json_file)


def lines_set_from_bytes(data):
    return set(data.decode('utf-8').strip().split('\n'))


def lines_bytes_from_set(given_set):
    return "\n".join(given_set)


def update_json_file():
    with open(path.join(SCRIPT_DIR_PATH, HM_PKGS_DIR ,JSON_FILE), 'w') as json_file:
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
        print("[X] Failed to properly decompress '" + zip_name + "'\n exiting...")
        exit()


def auto_install(required_tools):
    makedirs(TOOLS_DIR, exist_ok=True)
    for tool in required_tools:
        if tools[tool]["install_type"] == "compiled":
            try:
                install_compiled(tool)
            except Exception as e:
                print("[X] The following exception occured when installing '" + tool + "':")
                print(e)
                exit()
        elif tools[tool]["install_type"] == "from_repo":
            try:
                install_from_repo(tool)
            except Exception as e:
                print("[X] The following exception occured when installing '" + tool + "':")
                print(e)
                exit()


def available_in_apt(pkg_name):
    return apt.Cache().get(pkg_name) is not None


def tool_exists(tool):
    return which(tool) is not None or path.exists(tool)


def ask_for_path(tool):
    while True:
        path = input("[?] Please enter the full path for '" + tool + "': ")
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
                deb_pkg = path.join(TOOLS_DIR, "google-chrome.deb")
                wget.download("https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", deb_pkg)
                install_browser("./" + deb_pkg)
                return
        elif choice.upper() == 'N':
            print("[!] Install 'google-chrome' or 'chromium-browser' manually, or run the script again. Bye!")
            exit()
        else:
            print("[!] Please enter 'Y' or 'N' only.")


def warn_missing(missing_tools):
    for missing in missing_tools:
        print("[!] missing tool: '" + missing + "'")


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


def verify_reachable_targets(target_arg):
    for target in target_arg.split(','):
        if not reachable(target):
            print("[X] Problem with reaching target: '" + target + "'")
            exit()


def verify_targets_format(target_arg):
    for target in target_arg.split(','):
            if not is_valid_domain_format(target):
                print("[X] The target: '" + target + "' is not a valid domain format. Make sure to use a valid domain with no schema")
                exit()


def raw_subdomains(target_arg, token):
    print("[+] Firing 'Amass' to hunt subdomains...")
    time.sleep(1)
    amass_proc = amass(tools['amass']["path"], target_arg)

    print("[+] Hunting subdomains on GitHub...")
    time.sleep(1)
    github_subdoms = ''
    for target in target_arg.split(','):
        print("[+] Waiting for Amass...")
        result = github_subdomains(tools['github-subdomains']["path"], target, token) 
        print("[+] Attempted to find subdomains on github for '" + target + "':")
        print(result)
        github_subdoms += result
        time.sleep(1)
    print("[+] Finished enumerating github. Waiting for Amass to finish...")
    
    amass_proc.wait()
    print("[+] Retrived Amass subdomains:")
    amass_subdoms = amass_subdomains(tools['amass']["path"], target_arg)
    print(amass_subdoms)

    # write individual subdomain enum results to files
    print("[+] Writing enumeration results to files...")
    time.sleep(1)
    with open(path.join(RES_ROOT_DIR, SUB_GIT_FILE), 'w') as f:
        f.write(github_subdoms)
    with open(path.join(RES_ROOT_DIR, SUB_AMASS_FILE), 'w') as f:
        f.write(amass_subdoms)

    # return only valid domain formats from scan results
    subdoms = lines_set_from_bytes(bytes(amass_subdoms + github_subdoms))
    return set(subdom for subdom in subdoms if is_valid_domain_format(subdom))


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
            print('[+] removed: ' + subdomain)

    # store results in file
    print("[+] Writing resolvable subdomains with unique destinations to files...")
    time.sleep(1)
    with open(path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE), 'w') as f:
        f.write('\n'.join(unique_dest_set) + '\n')
        
    return unique_dest_set


def start_sequence(target_arg, github_token, blacklist_arg):
    print("\n\n[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    print("\n\n[+] Hunting live subdomains initiated")
    time.sleep(2)

    # Collect subdomains list with unique destinations
    target_domains = set(target_arg.split(','))
    unique_subdomains = raw_subdomains(target_arg, github_token)
    target_domains.update(unique_subdomains)
    remove_blacklist(blacklist_arg, target_domains)
    live_targets = unique_live_targets(target_domains)
    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)

    print("[+] Firing 'Aquatone' to screen web apps...")
    time.sleep(1)
    aquatone_proc = aquatone(tools['aquatone']["path"])

    print("[+] Firing 'Subdomainizer' to hunt stored secrets...")
    time.sleep(1)
    subdomainizer_proc = subdomainizer(tools['subdomainizer']["path"], github_token)

    aquatone_proc.wait()
    subdomainizer_proc.wait()

    print("\n\n[+] 'HUNTSMAN' sequence completed")
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
        print('[!] usage:')
        print('\n    ' + arg[0] + ' TARGET_DOMAINS' +
              ' GITHUB_TOKEN' + ' [DOMAIN_BLACKLIST]')
        print('\n[!] comma separate multi-inputs')
        exit()

    # validating provided inputs
    verify_github_token(github_token)
    verify_targets_format(target_arg)

    check_for_tools()

    # checking for previous runs of 'Huntsman'
    if path.isdir(RES_ROOT_DIR):
        print('Results directory exists. exiting to avoid loss of previous reports...')
        exit()
    else:
        mkdir(RES_ROOT_DIR)

    start_sequence(target_arg, github_token, blacklist_arg)

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
