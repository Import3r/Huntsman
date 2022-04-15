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

    # release subdom hounds to collect subdomains
    hound_batch = {"amass", "assetfinder", "github_dorkers"}
    HM.release_batch(hound_batch)
    HM.merge_outfiles(hound_batch, HM.raw_subdom_file)

    HM.release_batch({"massdns"})  # resolve collected raw subdomains
    HM.release_batch({"httprobe"})  # filter resolved subdomains with live web apps
    HM.release_batch({"aquatone"})  # screenshot the live web apps
    
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
