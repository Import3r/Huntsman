#! /usr/bin/python3

from packages.Hunt import Hunt
from packages.Huntsman import Huntsman
from os import setpgrp, killpg 
from packages.common_utils import concat_uniqe_lines
import time, signal

banner = """

▒█░▒█ █░░█ █▀▀▄ ▀▀█▀▀ █▀▀ █▀▄▀█ █▀▀█ █▀▀▄ 
▒█▀▀█ █░░█ █░░█ ░░█░░ ▀▀█ █░▀░█ █▄▄█ █░░█ 
▒█░▒█ ░▀▀▀ ▀░░▀ ░░▀░░ ▀▀▀ ▀░░░▀ ▀░░▀ ▀░░▀

"""


def main():
    print(banner)

    operation = Hunt()

    operation.check_arguments()
    operation.validate_arguments()
    
    HM = Huntsman(operation)
    HM.ensure_hounds()

    print("\n\n[+] Ready to engage.\n\n")
    time.sleep(1)

    print("[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    thread_pool = set()

    # release subdom hounds to collect subdomains
    hound_batch = {"amass", "assetfinder", "github_dorkers"}
    for h in hound_batch:
        thread_pool.add( HM.activate_hound(h) )

    # wait for subhunters to finish collecting raw subdomains
    for t in thread_pool: t.join()
    thread_pool.clear()

    HM.merge_outfiles(hound_batch, HM.raw_subdom_file)

    thread_pool.add( HM.activate_hound("waybackurls") )
    HM.activate_hound("massdns").join()  # wait for MassDNS to resolve raw subdomains
    HM.activate_hound("httprobe").join()  # filter resolved subdomains with live web apps
    HM.activate_hound("aquatone").join()  # screenshot live web apps 
    thread_pool.add( HM.activate_hound("gospider") )
    
    # wait for running hounds
    for t in thread_pool: t.join()
    thread_pool.clear()

    HM.merge_outfiles({"gospider", "waybackurls"}, HM.raw_ep_file)
    
    print("[+] 'HUNTSMAN' sequence completed")
    time.sleep(2)

    print("[+] Operation succeeded. All results are stored at '" + operation.res_root_dir + "'.")
    time.sleep(1)
    print("[+] Shutting down...")
    time.sleep(2)


# calling main while handling KeyboardInterrupts
try:
    setpgrp()
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("\n\n[!] Exiting...")
    killpg(0, signal.SIGKILL)
