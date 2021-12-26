#! /usr/bin/python3

from os import path
from sys import argv

HM_STORAGE_DIR_NAME = 'assets'
HM_STORAGE_DIR = HM_STORAGE_DIR_NAME

INST_TOOLS_DIR_NAME = 'installed_tools'
INST_TOOLS_DIR = path.join(HM_STORAGE_DIR, INST_TOOLS_DIR_NAME)
HM_WORDLISTS_DIR_NAME = 'wordlists'
HM_WORDLISTS_DIR = path.join(HM_STORAGE_DIR, HM_WORDLISTS_DIR_NAME)

RES_ROOT_DIR_NAME = 'huntsman_results'
RES_ROOT_DIR = RES_ROOT_DIR_NAME

SUB_HOUND_RES_DIR_NAME = 'collected_subdomains'
SUB_HOUND_RES_DIR = path.join(RES_ROOT_DIR, SUB_HOUND_RES_DIR_NAME)
SUB_ALL_RAW_FILE_NAME = 'raw-subdomains.all'
SUB_ALL_RAW_FILE = path.join(SUB_HOUND_RES_DIR, SUB_ALL_RAW_FILE_NAME)
SUB_ALL_RSLVD_FILE_NAME = 'resolved-subdomains.all'
SUB_ALL_RSLVD_FILE = path.join(SUB_HOUND_RES_DIR, SUB_ALL_RSLVD_FILE_NAME)

ENDP_HOUND_RES_DIR_NAME = 'collected_endpoints'
ENDP_HOUND_RES_DIR = path.join(RES_ROOT_DIR, ENDP_HOUND_RES_DIR_NAME)
ENDP_ALL_RAW_FILE_NAME = 'raw-endpoints.all'
ENDP_ALL_RAW_FILE = path.join(ENDP_HOUND_RES_DIR, ENDP_ALL_RAW_FILE_NAME)

PATHS_JSON_FILE_NAME = '.inst_tools_paths.json'
PATHS_JSON_FILE = path.join(path.dirname(argv[0]), PATHS_JSON_FILE_NAME)