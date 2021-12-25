#! /usr/bin/python3

from packages.static_paths import ENDP_MASTER_FILE
from packages.common_utils import *
import packages.tools_loader
import time


def activate(subdomains, subdoms_file):
    print("\n\n[+] Hunting endpoints for targets initiated")
    time.sleep(2)
    
    print("[+] Firing 'gospider' to hunt endpoints...")
    time.sleep(1)
    gospider = packages.tools_loader.loaded_tools["gospider"]
    gospider_proc = gospider.crawler_proc(subdomains)
    
    print("[+] Firing 'waybackurls' to hunt endpoints...")
    time.sleep(1)
    wayback = packages.tools_loader.loaded_tools["waybackurls"]
    wayback_proc = wayback.enumerator_proc(subdoms_file)

    wayback_output = wayback_proc.communicate()[0].decode('utf-8')
    wayback_endpoints = lines_set_from_bytes(bytes(wayback_output, 'utf-8'))

    gospider_output = gospider_proc.communicate()[0].decode('utf-8')
    gospider_endpoints = lines_set_from_bytes(bytes(gospider_output, 'utf-8'))

    all_endpoints = wayback_endpoints.union(gospider_endpoints)

    print("[+] Retrieved endpoints:\n")
    endpoints_data = lines_data_from_set(all_endpoints)
    print(endpoints_data)

    store_results(endpoints_data, ENDP_MASTER_FILE)

    print("\n\n[+] Hunting endpoints for targets completed")
    time.sleep(2)

    return all_endpoints