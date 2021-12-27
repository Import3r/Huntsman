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
        dorkers_proc = github_dorkers.enumerator_proc(target, github_token) 
        result = dorkers_proc.communicate()[0].decode('utf-8')
        print("[+] Attempted to find subdomains on github for '" + target + "':")
        print(result)
        github_output += result
        time.sleep(1)
    
    store_results(github_output, github_dorkers.output_file)
    github_subdoms = set_of_lines_from_text(github_output)

    print("[+] Finished enumerating github. Waiting for Amass to finish...")
    amass_output = amass_proc.communicate()[0].decode('utf-8')
    print("[+] Retrieved Amass subdomains:\n")
    print(amass_output)
    store_results(amass_output, amass.output_file)
    amass_subdoms = set_of_lines_from_text(amass_output)

    # clean-up non-valid domain formats from scan results
    valid_format_subdoms = set(subdom for subdom in github_subdoms.union(amass_subdoms) if is_valid_domain_format(subdom))
    targets.update(valid_format_subdoms)
    remove_blacklist(blacklist_targets, targets)
    store_results(text_from_set_of_lines(targets), SUB_ALL_RAW_FILE)
    
    massdns = packages.asset_loader.loaded_assets["massdns"]
    massdns_proc = massdns.subdom_resolver_proc(SUB_ALL_RAW_FILE)
    massdns_output = massdns_proc.communicate()[0].decode('utf-8')
    print("[+] Resolved the following subdomains:\n")
    print(massdns_output)
    store_results(massdns_output, SUB_ALL_RSLVD_FILE)
    resolved_subdoms = set_of_lines_from_text(massdns_output)
    
    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)
    
    return resolved_subdoms