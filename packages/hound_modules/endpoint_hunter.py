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
    
    gospider_thread = threading.Thread(target=gospider.thread_handler, args=(subdomains,))
    wayback_thread = threading.Thread(target=wayback.thread_handler, args=(subdoms_file,))

    gospider_thread.start()
    wayback_thread.start()

    gospider_thread.join()
    wayback_thread.join()

    gospider_endpoints = set_of_lines_from_text(gospider.output_buffer)
    wayback_endpoints = set_of_lines_from_text(wayback.output_buffer)
    all_endpoints = wayback_endpoints.union(gospider_endpoints)

    store_results(text_from_set_of_lines(all_endpoints), ENDP_ALL_RAW_FILE)

    print("\n\n[+] Hunting endpoints for targets completed\n\n")
    time.sleep(2)

    return all_endpoints