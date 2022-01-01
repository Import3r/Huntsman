#! /usr/bin/python3

from packages.static_paths import ENDP_HOUND_RES_DIR, ENDP_ALL_RAW_FILE
from packages.common_utils import set_of_lines_from_text, text_from_set_of_lines, store_results
import packages.asset_loader
from os import makedirs
import time, threading


def activate(subdomains, subdoms_file):
    makedirs(ENDP_HOUND_RES_DIR, exist_ok=True)
    
    print("\n\n[+] Hunting endpoints for targets initiated")
    time.sleep(2)

    gospider = packages.asset_loader.loaded_assets["gospider"]
    wayback = packages.asset_loader.loaded_assets["waybackurls"]
    
    print("[+] Firing 'gospider' to hunt endpoints...")
    time.sleep(1)
    gospider_thread = threading.Thread(target=gospider.thread_handler, args=(subdomains,))
    gospider_thread.start()
    
    print("[+] Firing 'waybackurls' to hunt endpoints...")
    time.sleep(1)
    wayback_thread = threading.Thread(target=wayback.thread_handler, args=(subdoms_file,))
    wayback_thread.start()

    gospider_thread.join()
    wayback_thread.join()

    gospider_endpoints = set_of_lines_from_text(gospider.output_buffer)
    wayback_endpoints = set_of_lines_from_text(wayback.output_buffer)
    all_endpoints = wayback_endpoints.union(gospider_endpoints)

    print("[+] Retrieved endpoints:\n")
    endpoints_data = text_from_set_of_lines(all_endpoints)
    print(endpoints_data)

    store_results(endpoints_data, ENDP_ALL_RAW_FILE)

    print("\n\n[+] Hunting endpoints for targets completed")
    time.sleep(2)

    return all_endpoints