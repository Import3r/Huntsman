#! /usr/bin/python3

from enum import unique
from packages.asset_modules.massdns_tool import MassDNS
from packages.static_paths import SUB_ALL_RAW_FILE, SUB_HOUND_RES_DIR, SUB_ALL_RSLVD_FILE
from packages.common_utils import *
import packages.asset_loader
from os import makedirs
import time


def activate(targets, github_token, blacklist_targets):
    makedirs(SUB_HOUND_RES_DIR, exist_ok=True)

    print("\n\n[+] Hunting live subdomains initiated")
    time.sleep(2)

    amass = packages.asset_loader.loaded_assets["amass"]
    github_dorkers = packages.asset_loader.loaded_assets["github_dorkers"]

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
    
    massdns = packages.asset_loader.loaded_assets["massdns"]

    targets.update(valid_format_subdoms)
    remove_blacklist(blacklist_targets, targets)
    store_results(lines_data_from_set(targets), SUB_ALL_RAW_FILE)
    massdns_proc = massdns.subdom_resolver_proc(SUB_ALL_RAW_FILE)
    unique_targets_data = massdns_proc.stdout
    # unique_targets= resolved_targets(targets)
    print("[+] Resolved the following subdomains:\n")
    print(unique_targets_data.decode("utf-8"))
    store_results(unique_targets_data.decode("utf-8"), SUB_ALL_RSLVD_FILE)
    unique_targets = lines_set_from_bytes(unique_targets_data)
    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)
    
    return unique_targets