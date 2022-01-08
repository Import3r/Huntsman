#! /usr/bin/python3

import json

class FileJSON:


    def __init__(self, file_path) -> None:
        self.file_path = file_path


    def read_data(self):
        try:
            with open(self.file_path, 'r') as json_file:
                paths = json.load(json_file)
            return paths
        except FileNotFoundError:
            return dict()


    def write_data(self, data):
        with open(self.file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)


    def read_value(self, key):
        try:
            with open(self.file_path, 'r') as json_file:
                return json.load(json_file).get(key, "")
        except FileNotFoundError:
            return ""


    def update_value(self, key, value):
        paths = self.read_data()
        paths[key] = value
        self.write_data(paths)
