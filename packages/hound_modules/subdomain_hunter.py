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

    print("\n\n[+] Hunting subdomains initiated\n\n")
    time.sleep(2)

    amass = packages.asset_loader.loaded_assets["amass"]
    github_dorkers = packages.asset_loader.loaded_assets["github_dorkers"]
    assetfinder = packages.asset_loader.loaded_assets["assetfinder"]
    massdns = packages.asset_loader.loaded_assets["massdns"]

    amass_thread = threading.Thread(target=amass.thread_handler, args=(targets,))
    af_thread = threading.Thread(target=assetfinder.thread_handler, args=(targets,)) 
    dorkers_thread = threading.Thread(target=github_dorkers.thread_handler, args=(targets, github_token,)) 
    massdns_thread = threading.Thread(target=massdns.thread_handler, args=(SUB_ALL_RAW_FILE,)) 

    amass_thread.start()
    af_thread.start()
    dorkers_thread.start()

    amass_thread.join()
    af_thread.join()
    dorkers_thread.join()

    amass_subdoms = set_of_lines_from_text(amass.output_buffer)
    af_subdoms = set_of_lines_from_text(assetfinder.output_buffer)
    github_subdoms = set_of_lines_from_text(github_dorkers.output_buffer)

    all_subdoms = amass_subdoms.union(github_subdoms, af_subdoms)

    # clean-up non-valid domain formats from scan results
    valid_format_subdoms = set(subdom for subdom in all_subdoms if is_valid_domain_format(subdom))
    targets.update(valid_format_subdoms)
    remove_blacklist(blacklist_targets, targets)
    store_results(text_from_set_of_lines(targets), SUB_ALL_RAW_FILE)
    
    massdns_thread.start()
    massdns_thread.join()

    resolved_subdoms = set_of_lines_from_text(massdns.output_buffer)
    
    print("\n\n[+] Hunting subdomains completed\n\n")
    time.sleep(2)
    
    return resolved_subdoms