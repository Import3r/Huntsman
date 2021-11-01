#! /usr/bin/python3

from resources.packages import *
from resources.static_names import *
from resources.tools import *


def lines_set_from_bytes(data):
    return set(data.decode('utf-8').strip().split('\n'))


def lines_bytes_from_set(given_set):
    return "\n".join(given_set)


def update_install_path(tool, given_path):
    full_path = path.abspath(given_path)
    tools[tool]["path"] = full_path
    chmod(full_path, 0o744)
    update_json_file()


def install_go_package(tool):
    url = tools[tool]["install_url"]
    install_path = path.join(TOOLS_DIR, tools[tool]["remote_repo_name"])
    file_name = tools[tool]["file_name"]
    binary_path = path.join(path.expanduser("~"),"go","bin",file_name)
    makedirs(install_path, exist_ok=True)
    run(f"GO111MODULE=on go get -u {url}", shell=True, stderr=STDOUT)

    if path.exists(binary_path):
        rename(binary_path, path.join(install_path, file_name))
        update_install_path(tool, path.join(install_path, file_name))
    else:
        print("[X] Failed to install '" + tool + "'\n exiting...")
        exit()


def install_repo_python3(tool):
    url = tools[tool]["install_url"]
    install_path = path.join(TOOLS_DIR, tools[tool]["remote_repo_name"])
    req_name = tools[tool]["req_file_name"]
    file_name = tools[tool]["file_name"]
    
    if not path.exists(install_path):
        git.cmd.Git(TOOLS_DIR).clone(url)
    run([executable, "-m", "pip", "install", "-r", path.join(install_path, req_name)], stderr=STDOUT)
    update_install_path(tool, path.join(install_path, file_name))


def install_compiled_zip(tool):
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
        try:
            if tools[tool]["install_type"] == "compiled":
                install_compiled_zip(tool)
            elif tools[tool]["install_type"] == "go_package":
                install_go_package(tool)
            elif tools[tool]["install_type"] == "from_repo":
                install_repo_python3(tool)        

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


def subdomainizer(subdomainizer_path):
    mkdir(path.join(RES_ROOT_DIR, SBDZ_RES_DIR))
    SUBDOMS_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_SUB_FILE)
    SECRETS_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_SECRET_FILE)
    CLOUD_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_CLOUD_FILE)
    return run_async([subdomainizer_path, "-l", path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE), "-o", SUBDOMS_FILE, "-sop", SECRETS_FILE, "-cop", CLOUD_FILE, "-k"])


def aquatone(aquatone_path):
    OUTPUT_DIR = path.join(RES_ROOT_DIR, AQUATONE_RES_DIR)
    SUBDOMAINS_FILE = path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE)
    return run_async([aquatone_path, "-scan-timeout", "500", "-threads", "1", "-out", OUTPUT_DIR], stdin=open(SUBDOMAINS_FILE, 'r'), stdout=DEVNULL)


def amass(amass_path, target_arg):
    return run_async(f"{amass_path} enum --passive -d {target_arg} -nolocaldb", shell=True, stdout=PIPE, stderr=DEVNULL)


def github_subdomains(gh_subdom_path, target, token):
    return run([gh_subdom_path, '-t', token, '-d', target], capture_output=True).stdout.decode('utf-8')


def subdomains_altdns(altdns_path, source_file, wordlist_path, output_file):
    return run([altdns_path, '-i', source_file, '-o', output_file, '-w', wordlist_path])


def gospider_endpoints(gospider_path, endpoints_list, output_dir):
    gospider_proc = run(f"{gospider_path} -S {endpoints_list} --other-source -t 20 -o {output_dir} -d 6 -q | grep -E -o '[a-zA-Z]+://[^\ ]+'", capture_output=True, shell=True)
    return lines_set_from_bytes(gospider_proc.stdout)


def waybackurls_endpoints(wayback_path, target_doms, output_file):
    input_data = lines_bytes_from_set(target_doms)
    wayback_proc = run(f"{wayback_path} | tee {output_file}", capture_output=True, shell=True, input=input_data)
    return lines_set_from_bytes(wayback_proc.stdout)


def raw_subdomains(targets, token):
    print("[+] Firing 'Amass' to hunt subdomains...")
    time.sleep(1)

    amass_proc = amass(tools['amass']["path"], ','.join(targets))

    print("[+] Hunting subdomains on GitHub...")
    time.sleep(1)
    github_subdoms = ''
    for target in targets:
        print("[+] Waiting for Amass...")
        result = github_subdomains(tools['github-subdomains']["path"], target, token) 
        print("[+] Attempted to find subdomains on github for '" + target + "':")
        print(result)
        github_subdoms += result
        time.sleep(1)

    print("[+] Finished enumerating github. Waiting for Amass to finish...")
    amass_subdoms = amass_proc.communicate()[0].decode('utf-8')

    print("[+] Retrived Amass subdomains:")
    print(amass_subdoms)

    # write individual subdomain enum results to files
    print("[+] Writing enumeration results to files...")
    time.sleep(1)
    with open(path.join(RES_ROOT_DIR, SUB_GIT_FILE), 'w') as f:
        f.write(github_subdoms)
    with open(path.join(RES_ROOT_DIR, SUB_AMASS_FILE), 'w') as f:
        f.write(amass_subdoms)

    # return only valid domain formats from scan results
    subdoms = lines_set_from_bytes(bytes(amass_subdoms + github_subdoms, 'utf-8'))
    return set(subdom for subdom in subdoms if is_valid_domain_format(subdom))


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

    # store results in file
    print("[+] Writing resolvable subdomains with unique destinations to files...")
    time.sleep(1)
    with open(path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE), 'w') as f:
        f.write('\n'.join(unique_dest_set) + '\n')
        
    return unique_dest_set


def start_sequence(targets, github_token, blacklist_targets):
    print("\n\n[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    print("\n\n[+] Hunting live subdomains initiated")
    time.sleep(2)

    # Collect subdomains list with unique destinations
    target_domains = targets
    unique_subdomains = raw_subdomains(targets, github_token)
    target_domains.update(unique_subdomains)
    remove_blacklist(blacklist_targets, target_domains)
    live_targets = resolved_targets(target_domains)

    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)

    print("[+] Firing 'Aquatone' to screen web apps...")
    time.sleep(1)
    aquatone_proc = aquatone(tools['aquatone']["path"])

    print("[+] Firing 'Subdomainizer' to hunt stored secrets...")
    time.sleep(1)
    subdomainizer_proc = subdomainizer(tools['subdomainizer']["path"])

    aquatone_proc.wait()
    subdomainizer_proc.wait()

    print("\n\n[+] 'HUNTSMAN' sequence completed")
    time.sleep(1)


