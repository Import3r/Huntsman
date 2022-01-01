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
    hunting_hounds = (amass, github_dorkers, assetfinder)

    amass_thread = threading.Thread(target=amass.thread_handler, args=(targets,))
    af_thread = threading.Thread(target=assetfinder.thread_handler, args=(targets,)) 
    dorkers_thread = threading.Thread(target=github_dorkers.thread_handler, args=(targets, github_token,))
    hunting_threads = (amass_thread, af_thread, dorkers_thread)

    for t in hunting_threads: t.start()
    for t in hunting_threads: print("[+] 'HUNTSMAN' sequence in progress...\n\n"); t.join()

    # returns set of lines for each hound's results and joins them
    all_subdoms = set().union(*[hound.results_set for hound in hunting_hounds])

    targets.update(all_subdoms)
    remove_blacklist(blacklist_targets, targets)
    store_results(text_from_set_of_lines(targets), SUB_ALL_RAW_FILE)
    
    massdns = packages.asset_loader.loaded_assets["massdns"]
    massdns_thread = threading.Thread(target=massdns.thread_handler, args=(SUB_ALL_RAW_FILE,)) 

    massdns_thread.start()
    massdns_thread.join()

    resolved_subdoms = massdns.results_set
    
    print("\n\n[+] Hunting subdomains completed\n\n")
    time.sleep(2)
    
    return resolved_subdoms