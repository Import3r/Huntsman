#! /usr/bin/python3

from sys import executable, path as here, argv as arg
from subprocess import run, PIPE, DEVNULL, STDOUT, Popen as run_async
from shutil import which
from os import path, chmod, makedirs, mkdir, geteuid, getcwd, setpgrp, killpg, devnull
import apt
import git
import wget
import zipfile
import requests
import json
import re
import time
import signal