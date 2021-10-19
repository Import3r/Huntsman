#! /usr/bin/python3

from resources.packages import *
from resources.static_names import *

def subdomainizer(subdomainizer_path, github_token):
    mkdir(path.join(RES_ROOT_DIR, SBDZ_RES_DIR))
    SUBDOMS_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_SUB_FILE)
    SECRETS_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_SECRET_FILE)
    CLOUD_FILE = path.join(RES_ROOT_DIR, SBDZ_RES_DIR, SBDZ_CLOUD_FILE)
    return run_async([subdomainizer_path, "-l", path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE), "-o", SUBDOMS_FILE, "-sop", SECRETS_FILE, "-cop", CLOUD_FILE, "-k", "-g", "-gt", github_token])


def aquatone(aquatone_path):
    OUTPUT_DIR = path.join(RES_ROOT_DIR, AQUATONE_RES_DIR)
    SUBDOMAINS_FILE = path.join(RES_ROOT_DIR, UNIQUE_SUB_FILE)
    return run_async([aquatone_path, "-scan-timeout", "500", "-threads", "1", "-out", OUTPUT_DIR], stdin=open(SUBDOMAINS_FILE, 'r'), stdout=open(devnull, 'w'))


def amass(amass_path, target_arg):
    return run_async([amass_path, "enum", "-d", target_arg])


def github_subdomains(gh_subdom_path, target, token):
    return run([gh_subdom_path, '-t', token, '-d', target], capture_output=True).stdout.decode('utf-8')


def amass_subdomains(amass_path, target_arg):
    return run([amass_path, 'db', '-d', target_arg, '--names'], capture_output=True).stdout.decode('utf-8')
