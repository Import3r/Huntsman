#! /usr/bin/python3

from packages.static_paths import ENDP_HOUND_RES_DIR, ENDP_ALL_RAW_FILE
from packages.common_utils import set_of_lines_from_text, text_from_set_of_lines, store_results
import packages.asset_loader
from os import makedirs
import time, threading


def activate(subdomains, subdoms_file):
    makedirs(ENDP_HOUND_RES_DIR, exist_ok=True)
    
    print("\n\n[+] Hunting endpoints for targets initiated\n\n")
    time.sleep(2)

    gospider = packages.asset_loader.loaded_assets["gospider"]
    wayback = packages.asset_loader.loaded_assets["waybackurls"]
    hunting_hounds = (gospider, wayback)

    gospider_thread = threading.Thread(target=gospider.thread_handler, args=(subdomains,))
    wayback_thread = threading.Thread(target=wayback.thread_handler, args=(subdoms_file,))
    hunting_threads = (gospider_thread, wayback_thread)

    for t in hunting_threads: t.start()
    for t in hunting_threads: print("[+] 'HUNTSMAN' sequence in progress...\n\n"); t.join()
    
    all_endpoints = set().union(*[hound.results_set for hound in hunting_hounds])

    qsreplace = packages.asset_loader.loaded_assets["qsreplace"]
    qsreplace_thread = threading.Thread(target=qsreplace.thread_handler, args=(all_endpoints,))
    
    qsreplace_thread.start()
    qsreplace_thread.join()
    
    unique_endpoints = qsreplace.results_set
    
    print("\n\n[+] Hunting endpoints for targets completed\n\n")
    time.sleep(2)

    return unique_endpoints