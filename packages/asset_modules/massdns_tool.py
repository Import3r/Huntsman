#! /usr/bin/python3

from shutil import which
from packages.common_utils import store_results, text_from_set_of_lines, set_of_lines_from_text, is_valid_domain_format
from os import chmod, path, makedirs
from subprocess import run, Popen, PIPE, DEVNULL
import zipfile, wget


class MassDNS:
    asset_name = "massdns"
    remote_repo_name = "massdns"
    zipfile_name = "massdns.zip"
    compiled_zip_url = "https://github.com/blechschmidt/massdns/archive/refs/tags/v1.0.0.zip"
    dns_resolvers_list = ""


    def __init__(self, operation) -> None:
        self.paths_file = operation.paths_json_file
        self.asset_path = self.paths_file.read_value(self.asset_name)
        self.install_path = path.join(operation.inst_tools_dir, self.remote_repo_name)
        self.output_buffer = ""
        self.results_set = set()


    def update_install_path(self, new_path):
        self.asset_path = path.abspath(new_path)
        chmod(self.asset_path, 0o744)
        self.paths_file.update_value(self.asset_name, self.asset_path)


    def is_installed(self):
        return which(self.asset_path) is not None or path.exists(self.asset_path)


    def install(self):       
        makedirs(self.install_path, exist_ok=True)
        zip_path = path.join(self.install_path, self.zipfile_name)
        if not path.exists(zip_path):
            wget.download(self.compiled_zip_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(self.install_path)
            zip_root_dir_name = zip_file.namelist()[0]
            unzipped_dir = path.join(self.install_path, zip_root_dir_name)
        
        if path.exists(unzipped_dir):
            run(f"make -C {unzipped_dir}", shell=True)
            self.update_install_path(path.join(unzipped_dir, 'bin', self.asset_name))
        else:
            print("[X] Failed to properly decompress '" + self.zipfile_name + "'\nexiting...")
            exit()


    def subdom_resolver_proc(self, domains_file):
        return Popen(f"{self.asset_path} -r {self.dns_resolvers_list} -t AAAA {domains_file} -o S | grep -oE '^([A-Za-z0-9\-]+\.)*[A-Za-z0-9\-]+\.[A-Za-z0-9]+' | sort -u", shell=True, stdout=PIPE, stderr=DEVNULL)


    def thread_handler(self, domains_file, dns_resolver, sub_all_resolved_file):
        print("[+] Firing 'MassDNS' to resolve collected subdomains...")
        self.dns_resolvers_list = dns_resolver.location()
        massdns_proc = self.subdom_resolver_proc(domains_file)
        self.output_buffer = massdns_proc.communicate()[0].decode("utf-8")
        print("[+] MassDNS resolved the following subdomains:", self.output_buffer, sep='\n\n')
        # clean up duplicates and non-valid domain formats from output before storing results
        self.results_set = set(subdom for subdom in set_of_lines_from_text(self.output_buffer) if is_valid_domain_format(subdom))
        store_results(text_from_set_of_lines(self.results_set), sub_all_resolved_file)
        print("[+] Resolving subdomains completed")
