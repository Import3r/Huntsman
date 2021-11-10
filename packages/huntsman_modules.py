#! /usr/bin/python3

from packages.static_paths import SUB_MASTER_FILE, ENDP_MASTER_FILE
from packages.common_utils import *
import packages.tools_loader
from subprocess import run
import time


def subdomains_altdns(altdns_path, source_file, wordlist_path, output_file):
    return run([altdns_path, '-i', source_file, '-o', output_file, '-w', wordlist_path])


def raw_subdomains(amass, github_dorkers, targets, token):
    print("[+] Firing 'Amass' to hunt subdomains...")
    time.sleep(1)
    amass_proc = amass.enumerator_proc(targets)

    print("[+] Hunting subdomains on GitHub...")
    time.sleep(1)
    github_output = ''
    for target in targets:
        print("[+] Waiting for Amass...")
        result = github_dorkers.subdomains(target, token) 
        print("[+] Attempted to find subdomains on github for '" + target + "':")
        print(result)
        github_output += result
        time.sleep(1)
    github_subdoms = lines_set_from_bytes(bytes(github_output, 'utf-8'))

    print("[+] Finished enumerating github. Waiting for Amass to finish...")
    amass_output = amass_proc.communicate()[0].decode('utf-8')

    print("[+] Retrieved Amass subdomains:\n")
    print(amass_output)
    amass_subdoms = lines_set_from_bytes(bytes(amass_output, 'utf-8'))

    # return only valid domain formats from scan results
    all_valid_subdoms = set(subdom for subdom in github_subdoms.union(amass_subdoms) if is_valid_domain_format(subdom))
    return (all_valid_subdoms, amass_subdoms, github_subdoms)


def endpoint_hunter_module(subdomains, subdoms_file):
    print("[+] Firing 'gospider' to hunt endpoints...")
    time.sleep(1)
    gospider = packages.tools_loader.gospider
    gospider_proc = gospider.crawler_proc(subdomains)
    
    print("[+] Firing 'waybackurls' to hunt endpoints...")
    time.sleep(1)
    wayback = packages.tools_loader.waybackurls
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

    return all_endpoints


def subdomain_hunter_module(targets, github_token, blacklist_targets):
    amass = packages.tools_loader.amass
    github_dorkers = packages.tools_loader.github_dorkers

    # Collect subdomains list with unique destinations
    all_subdomains, amass_subdoms, github_subdoms = raw_subdomains(amass, github_dorkers, targets, github_token)
    
    targets.update(all_subdomains)
    remove_blacklist(blacklist_targets, targets)
    unique_targets = resolved_targets(targets)
    
    # write each individual result to files
    print("[+] Writing enumeration results to files...")
    time.sleep(1)
    store_results(lines_data_from_set(github_subdoms), github_dorkers.output_file)
    store_results(lines_data_from_set(amass_subdoms), amass.output_file)
    store_results(lines_data_from_set(unique_targets), SUB_MASTER_FILE)
    return unique_targets


def start_sequence(targets, github_token, blacklist_targets):
    print("\n\n[+] Hunting live subdomains initiated")
    time.sleep(2)

    all_subdomains = subdomain_hunter_module(targets, github_token, blacklist_targets)

    print("\n\n[+] Hunting live subdomains completed")
    time.sleep(2)

    print("[+] Firing 'Aquatone' to screen web apps...")
    time.sleep(1)
    aquatone = packages.tools_loader.aquatone
    aquatone_proc = aquatone.snapper_proc(SUB_MASTER_FILE)

    print("[+] Firing 'Subdomainizer' to hunt stored secrets...")
    time.sleep(1)
    subdomainizer = packages.tools_loader.subdomainizer
    subdomainizer_proc = subdomainizer.scraper_proc(SUB_MASTER_FILE)

    print("\n\n[+] Hunting endpoints for targets initiated")
    time.sleep(2)

    all_endpoints = endpoint_hunter_module(all_subdomains, SUB_MASTER_FILE)

    print("\n\n[+] Hunting endpoints for targets completed")
    time.sleep(2)

    aquatone_proc.wait()
    subdomainizer_proc.wait()
