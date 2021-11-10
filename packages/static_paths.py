#! /usr/bin/python3

from os import path
from sys import argv

PATHS_JSON_FILE_NAME = 'tools_paths.json'
HM_STORAGE_DIR_NAME = 'storage'
RES_ROOT_DIR_NAME = 'huntsman_results'
INST_TOOLS_DIR_NAME = 'installed_tools'
SUB_MASTER_FILE_NAME = 'subdomains.all'
ENDP_MASTER_FILE_NAME = 'endpoints.all'

PATHS_JSON_FILE = path.join(path.dirname(argv[0]), HM_STORAGE_DIR_NAME, PATHS_JSON_FILE_NAME)
RES_ROOT_DIR = RES_ROOT_DIR_NAME
ENDP_MASTER_FILE = path.join(RES_ROOT_DIR_NAME, ENDP_MASTER_FILE_NAME)
SUB_MASTER_FILE = path.join(RES_ROOT_DIR_NAME, SUB_MASTER_FILE_NAME)
INST_TOOLS_DIR = path.join(HM_STORAGE_DIR_NAME, INST_TOOLS_DIR_NAME)