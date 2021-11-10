#! /usr/bin/python3

from packages.package_imports import *


def read_from(json_path):
    try:
        with open(json_path, 'r') as json_file:
            paths = json.load(json_file)
        return paths
    except FileNotFoundError:
        return dict()

def write_data_to(json_path, data):
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)