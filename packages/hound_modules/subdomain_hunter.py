#! /usr/bin/python3

from enum import unique
from packages.asset_modules.massdns_tool import MassDNS
from packages.static_paths import SUB_ALL_RAW_FILE, SUB_HOUND_RES_DIR, SUB_ALL_RSLVD_FILE
from packages.common_utils import *
import packages.asset_loader
from os import makedirs
import time, threading


def activate(targets, github_token, blacklist_targets):
    makedirs(SUB_HOUND_RES_DIR, exist_ok=True)

    print("\n\n[+] Hunting live subdomains initiated")
    time.sleep(2)

    amass = packages.asset_loader.loaded_assets["amass"]
    github_dorkers = packages.asset_loader.loaded_assets["github_dorkers"]
    assetfinder = packages.asset_loader.loaded_assets["assetfinder"]
    massdns = packages.asset_loader.loaded_assets["massdns"]

    print("[+] Firing 'Amass' to hunt subdomains...")
    time.sleep(1)
    amass_thread = threading.Thread(target=amass.thread_handler, args=(targets,))
    amass_thread.start()

    print("[+] Firing 'assetfinder' to hunt subdomains...")
    time.sleep(1)
    af_thread = threading.Thread(target=assetfinder.thread_handler, args=(targets,)) 
    af_thread.start()

    print("[+] Hunting subdomains on GitHub...")
    time.sleep(1)
    dorkers_thread = threading.Thread(target=github_dorkers.thread_handler, args=(targets, github_token,)) 
    dorkers_thread.start()

    amass_thread.join()
    af_thread.join()
    dorkers_thread.join()

    print("[+] Retrieved Amass subdomains:\n")
    print(amass.output_buffer)

    store_results(amass.output_buffer, amass.output_file)
    amass_subdoms = set_of_lines_from_text(amass.output_buffer)
    store_results(assetfinder.output_buffer, assetfinder.output_file)
    af_subdoms = set_of_lines_from_text(assetfinder.output_buffer)
    store_results(github_dorkers.output_buffer, github_dorkers.output_file)
    github_subdoms = set_of_lines_from_text(github_dorkers.output_buffer)

    all_subdoms = amass_subdoms.union(github_subdoms, af_subdoms)

    # clean-up non-valid domain formats from scan results
    valid_format_subdoms = set(subdom for subdom in all_subdoms if is_valid_domain_format(subdom))
    targets.update(valid_format_subdoms)
    remove_blacklist(blacklist_targets, targets)
    store_results(text_from_set_of_lines(targets), SUB_ALL_RAW_FILE)
    
    massdns_thread = threading.Thread(target=massdns.thread_handler, args=(SUB_ALL_RAW_FILE,)) 
    massdns_thread.start()
    massdns_thread.join()

    print("[+] Resolved the following subdomains:\n")
    print(massdns.output_buffer)
    store_results(massdns.output_buffer, SUB_ALL_RSLVD_FILE)
    resolved_subdoms = set_of_lines_from_text(massdns.output_buffer)
    
    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)
    
    return resolved_subdoms