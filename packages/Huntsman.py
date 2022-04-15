#! /usr/bin/python3

from packages.asset_modules.amass_tool import Amass
from packages.asset_modules.aquatone_tool import Aquatone
from packages.asset_modules.assetfinder_tool import AssetFinder
from packages.asset_modules.github_dorkers_tool import GithubDorkers
from packages.asset_modules.massdns_tool import MassDNS
from packages.asset_modules.gospider_tool import GoSpider
from packages.asset_modules.httprobe_tool import HttProbe
from packages.asset_modules.qsreplace_tool import QSReplace
from packages.asset_modules.subdomainizer_tool import Subdomainizer
from packages.asset_modules.waybackurls_tool import Waybackurls
from packages.asset_modules.dns_resolvers_ip_list import DNSResolversList
from os import makedirs, path
from packages.common_utils import concat_uniqe_lines
from packages.install_handler import get_valid_path, prompt_decision
import threading


class Huntsman:
    subdom_results_dir_name = 'collected_subdomains'
    ep_results_dir_name = 'collected_endpoints'
    
    raw_subdom_file_name = 'raw-subdomains.all'
    raw_ep_file_name = 'raw-endpoints.all'

    resolved_subdom_file_name = 'resolved-subdomains.all'
    base_live_ep_file_name = 'base-live-endpoints.all'


    def __init__(self, operation) -> None:
        self.operation = operation
        self.subdom_results_dir = path.join(operation.res_root_dir, self.subdom_results_dir_name)
        self.ep_results_dir = path.join(operation.res_root_dir, self.ep_results_dir_name)
        self.raw_subdom_file = path.join(self.subdom_results_dir, self.raw_subdom_file_name)
        self.raw_ep_file = path.join(self.ep_results_dir, self.raw_ep_file_name)
        self.resolved_subdom_file = path.join(self.subdom_results_dir, self.resolved_subdom_file_name)
        self.base_live_ep_file = path.join(self.ep_results_dir, self.base_live_ep_file_name)

        makedirs(self.subdom_results_dir, exist_ok=True)
        makedirs(self.ep_results_dir, exist_ok=True)

        self.hounds = {
            "amass" : Amass(operation, self.subdom_results_dir),
            "github_dorkers" : GithubDorkers(operation, self.subdom_results_dir),
            "assetfinder" : AssetFinder(operation, self.subdom_results_dir),
            "dns_resolvers_ip_list" : DNSResolversList(operation),
            "httprobe" : HttProbe(operation, self),
            "aquatone" : Aquatone(operation, self),
            "subdomainizer" : Subdomainizer(operation),
            "gospider" : GoSpider(operation, self.ep_results_dir),
            "waybackurls" : Waybackurls(operation, self.ep_results_dir),
            "qsreplace" : QSReplace(operation)
        }
        self.hounds["massdns"] = MassDNS(operation, self.hounds["dns_resolvers_ip_list"], self.raw_subdom_file ,self.resolved_subdom_file)


    def auto_install(self, hounds):
        makedirs(self.operation.inst_tools_dir, exist_ok=True)
        for hound in hounds:
            try:
                hound.install()
            except Exception as e:
                print("[X] The following exception occured when installing '" + hound.asset_name + "':", e, sep='\n')
                exit()


    def manual_install(self, hounds):
        choice_manual_inst = prompt_decision("[?] Would you like to enter the path for each asset you have manually? (Y)es, (N)o: ", ['Y', 'N'])        
        if choice_manual_inst == 'Y':
            for hound in hounds: hound.update_install_path(get_valid_path(hound.name))
        else:
            print("[!] Install the missing assets manually, or run the script again. Bye!")
            exit()


    def get_missing_hounds(self):
        missing = set()
        for hound in self.hounds.values():
            if not hound.is_installed():
                print("[!] missing asset: '" + hound.asset_name + "'")
                missing.add(hound)
        return missing


    def ensure_hounds(self):
        missing_hounds = self.get_missing_hounds()
        if missing_hounds:
            choice_auto_inst = prompt_decision("[?] Would you like me to pull the remaining assets for you? (Y)es, (N)o, (Q)uit: ", ['Y', 'N', 'Q'])
            if choice_auto_inst == 'Y': self.auto_install(missing_hounds)
            elif choice_auto_inst == 'N': self.manual_install(missing_hounds)
            else:
                print("[!] Install the missing assets manually, or run the script again. Bye!")
                exit()


    def release_batch(self, hound_names):
        for h in hound_names:
            if self.hounds.get(h) is None:
                raise Exception("Error: Unable to find '" + h + "' hound for release. Aborting...")
        
        thread_batch = set(self.hounds[hound].activate() for hound in hound_names)
        
        for t in thread_batch: t.join()


    def merge_outfiles(self, hound_names, dest_file_path):
        for h in hound_names:
            if self.hounds.get(h) is None:
                raise Exception("Error: Unable to find '" + h + "' hound for yielding. Aborting...")
        outfiles = set(self.hounds[hound].output_file for hound in hound_names)
        concat_uniqe_lines(outfiles, dest_file_path)