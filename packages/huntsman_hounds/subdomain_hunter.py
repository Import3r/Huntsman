#! /usr/bin/python3

from packages.static_paths import SUB_MASTER_FILE
from packages.common_utils import *
import packages.tools_loader
import time


def activate(targets, github_token, blacklist_targets):
    print("\n\n[+] Hunting live subdomains initiated")
    time.sleep(2)

    amass = packages.tools_loader.loaded_tools["amass"]
    github_dorkers = packages.tools_loader.loaded_tools["github_dorkers"]

    print("[+] Firing 'Amass' to hunt subdomains...")
    time.sleep(1)
    amass_proc = amass.enumerator_proc(targets)

    print("[+] Hunting subdomains on GitHub...")
    time.sleep(1)

    # Dork github for every given target to look for subdomains
    github_output = ''
    for target in targets:
        print("[+] Waiting for Amass...")
        result = github_dorkers.subdomains(target, github_token) 
        print("[+] Attempted to find subdomains on github for '" + target + "':")
        print(result)
        github_output += result
        time.sleep(1)
    
    github_subdoms = lines_set_from_bytes(bytes(github_output, 'utf-8'))
    store_results(lines_data_from_set(github_subdoms), github_dorkers.output_file)

    print("[+] Finished enumerating github. Waiting for Amass to finish...")
    amass_output = amass_proc.communicate()[0].decode('utf-8')

    print("[+] Retrieved Amass subdomains:\n")
    print(amass_output)
    amass_subdoms = lines_set_from_bytes(bytes(amass_output, 'utf-8'))
    store_results(lines_data_from_set(amass_subdoms), amass.output_file)

    # clean-up non-valid domain formats from scan results
    valid_format_subdoms = set(subdom for subdom in github_subdoms.union(amass_subdoms) if is_valid_domain_format(subdom))
    
    targets.update(valid_format_subdoms)
    remove_blacklist(blacklist_targets, targets)
    unique_targets = resolved_targets(targets)
    store_results(lines_data_from_set(unique_targets), SUB_MASTER_FILE)
    
    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)
    
    return unique_targets