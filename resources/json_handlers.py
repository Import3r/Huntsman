#! /usr/bin/python3

from resources.packages import *
from resources.static_names import *

with open(path.join(path.dirname(arg[0]), HM_PKGS_DIR ,TOOLS_JSON_FILE), 'r') as json_file:
    tools = json.load(json_file)

def update_json_file():
    with open(path.join(path.dirname(arg[0]), HM_PKGS_DIR ,TOOLS_JSON_FILE), 'w') as json_file:
        json.dump(tools, json_file, indent=4)