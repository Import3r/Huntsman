#! /usr/bin/python3

from resources.packages import *
from resources.static_names import RES_ROOT_DIR
from resources.utils import store_results, lines_data_from_set


class GoSpider:
    install_type = "go_package"
    exec_name = "gospider"
    results_dir_name = "gospider_results"
    input_file_name = "subdom-urls.temp"
    remote_repo_name = "gospider"
    remote_repo_url = "github.com/jaeles-project/gospider"


    def __init__(self, given_path) -> None:
        self.exec_path = given_path
        self.input_file = path.join(RES_ROOT_DIR, self.input_file_name)
        self.output_dir = path.join(RES_ROOT_DIR, self.results_dir_name)


    def crawler_proc(self, subdomains):
        base_endpoints = set("http://" + subdom for subdom in subdomains)
        store_results(lines_data_from_set(base_endpoints), self.input_file_name)
        return run_async(f"{self.exec_path} -S {self.input_file} --other-source -t 20 -o {self.output_dir} -d 6 -q | grep -E -o '[a-zA-Z]+://[^\ ]+'", shell=True, stdout=PIPE, stderr=DEVNULL)
