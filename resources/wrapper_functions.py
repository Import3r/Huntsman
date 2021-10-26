#! /usr/bin/python3

from sys import stdin
from resources.packages import *
from resources.static_names import *

from Huntsman import *

def subdomainizer(subdomainizer_path, github_token):
    mkdir(path.join(RES_ROOT_DIR, SBDZ_RES_DIR))
    SUBDOMS_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_SUB_FILE)
    SECRETS_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_SECRET_FILE)
    CLOUD_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_CLOUD_FILE)
    return run_async([subdomainizer_path, "-l", path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE), "-o", SUBDOMS_FILE, "-sop", SECRETS_FILE, "-cop", CLOUD_FILE, "-k", "-g", "-gt", github_token])


def aquatone(aquatone_path):
    OUTPUT_DIR = path.join(RES_ROOT_DIR, AQUATONE_RES_DIR)
    SUBDOMAINS_FILE = path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE)
    return run_async([aquatone_path, "-scan-timeout", "500", "-threads", "1", "-out", OUTPUT_DIR], stdin=open(SUBDOMAINS_FILE, 'r'), stdout=DEVNULL)


def amass(amass_path, target_arg):
    return run_async([amass_path, "enum", "-d", target_arg])


def github_subdomains(gh_subdom_path, target, token):
    return run([gh_subdom_path, '-t', token, '-d', target], capture_output=True).stdout.decode('utf-8')


def amass_subdomains(amass_path, target_arg):
    return run([amass_path, 'db', '-d', target_arg, '--names'], capture_output=True).stdout.decode('utf-8')


def subdomains_altdns(altdns_path, source_file, wordlist_path, output_file):
    return run([altdns_path, '-i', source_file, '-o', output_file, '-w', wordlist_path])


def gospider_endpoints(gospider_path, endpoints_list, output_dir):
    gospider_proc = run("{gospider_path} -S {endpoints_list} --other-source -t 20 -o {output_dir} -d 6 -q | grep -E -o '[a-zA-Z]+://[^\ ]+'", capture_output=True, shell=True)
    return lines_set_from_bytes(gospider_proc.stdout)


def waybackurls_endpoints(wayback_path, target_doms, output_file):
    input_data = lines_bytes_from_set(target_doms)
    wayback_proc = run("{wayback_path} | tee {output_file}", capture_output=True, shell=True, input=input_data)
    return lines_set_from_bytes(wayback_proc.stdout)

