#! /usr/bin/python3

from packages.Hunt import Hunt
from packages.Huntsman import Huntsman
from packages.static_paths import RES_ROOT_DIR, SUB_ALL_RSLVD_FILE
from os import setpgrp, killpg 
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
    
    HM = Huntsman(RES_ROOT_DIR, operation)
    HM.ensure_hounds()

    print("\n\n[+] Ready to engage.\n\n")
    time.sleep(1)

    print("[+] 'HUNTSMAN' sequence initiated")
    time.sleep(2)

    thread_batch = (
        HM.activate("amass", (operation.targets,)),
        HM.activate("assetfinder", (operation.targets,)),
        HM.activate("github_dorkers", (operation.targets, operation.github_token,)),
    )

    for t in thread_batch: t.join()
    
    # all_subdoms = set().union(*[hound.results_set for hound in subdom_hunters])
    # aquatone_thread = HM.activate("aquatone", (SUB_ALL_RSLVD_FILE,))
    # aquatone_thread.join()

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
