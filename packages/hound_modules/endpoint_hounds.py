#! /usr/bin/python3

from packages.static_paths import ENDP_HOUND_RES_DIR, ENDP_BASE_LIVE_FILE
import packages.asset_loader
from os import makedirs
import time, threading


def activate(subdomains, subdoms_file):
    makedirs(ENDP_HOUND_RES_DIR, exist_ok=True)
    
    print("\n\n[+] Hunting endpoints for targets initiated\n\n")
    time.sleep(2)

    wayback = packages.asset_loader.loaded_assets["waybackurls"]
    httprobe = packages.asset_loader.loaded_assets["httprobe"]

    wayback_thread = threading.Thread(target=wayback.thread_handler, args=(subdoms_file,))
    httprobe_thread = threading.Thread(target=httprobe.thread_handler, args=(subdomains,))

    for t in (httprobe_thread, wayback_thread): t.start()
    for t in (httprobe_thread, wayback_thread): print("[+] 'HUNTSMAN' sequence in progress...\n\n"); t.join()
    
    gospider = packages.asset_loader.loaded_assets["gospider"]
    subdomainizer = packages.asset_loader.loaded_assets["subdomainizer"]    
    
    gospider_thread = threading.Thread(target=gospider.thread_handler, args=(ENDP_BASE_LIVE_FILE,))
    subdomainizer_thread = threading.Thread(target=subdomainizer.thread_handler, args=(ENDP_BASE_LIVE_FILE,))
    
    for t in (gospider_thread, subdomainizer_thread): t.start()
    for t in (gospider_thread, subdomainizer_thread): print("[+] 'HUNTSMAN' sequence in progress...\n\n"); t.join()
    
    all_endpoints = set().union(*[hound.results_set for hound in (wayback, httprobe, gospider)])

    qsreplace = packages.asset_loader.loaded_assets["qsreplace"]
    qsreplace_thread = threading.Thread(target=qsreplace.thread_handler, args=(all_endpoints,))
    
    qsreplace_thread.start()
    qsreplace_thread.join()
    
    unique_endpoints = qsreplace.results_set
    
    print("\n\n[+] Hunting endpoints for targets completed\n\n")
    time.sleep(2)

    return unique_endpoints