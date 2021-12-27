#! /usr/bin/python3

import re, requests


def set_of_lines_from_text(given_text):
    return set(line for line in given_text.strip().split('\n') if line)


def text_from_set_of_lines(given_set):
    return "\n".join(given_set)


def store_results(data_string, file_path):
    with open(file_path, 'w') as f:
        f.write(data_string)


def remove_blacklist(blacklist, subdoms_set):
    # remove blacklisted assets
    subdoms_set.difference_update(blacklist)


def valid_github_token(github_token):
    return requests.get('https://api.github.com/user', headers={'authorization': 'Bearer ' + github_token}).ok


def is_valid_domain_format(string):
    return re.fullmatch('^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+$', string) != None


def reachable(target):
    url_regex = re.fullmatch('([A-Za-z]+:\/\/)*([A-Za-z0-9\-\.]+).*', target)
    target = url_regex[url_regex.lastindex]
    for method in ['http://', 'https://']:
        try:
            requests.head(method + target)
            return True
        except:
            pass
    return False


def resolved_targets(targets):
    # narrow down results to valid subdomains with unique destinations
    unique_dest_set = set()
    for subdomain in targets:
        try:
            response = requests.head("http://" + subdomain, allow_redirects=True)
            unique_dest_set.add(re.fullmatch('[A-Za-z]+:\/\/([A-Za-z0-9\-\.]+).*', response.url)[1])
            print('[+] resolved: ' + subdomain)
        except:
            print('[+] removed: ' + subdomain)
    return unique_dest_set
