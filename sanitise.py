#!/usr/bin/env python
"""
Script to sanitise text/content based on a set of rules
"""

# Python 3 support
from __future__ import absolute_import
from __future__ import print_function

__author__ = "Phuong Nguyen (pnguyen@redhat.com)"
__copyright__ = "Copyright 2020"
__version__ = "20201226"
__maintainer__ = "Phuong Nguyen"
__email__ = "pnguyen@redhat.com"
__status__ = "Development"

import six
import sys
import os
import yaml
import fileinput
import gzip
import bz2
from argparse import ArgumentParser

class Sanitiser(object):
    """
    Sanitises files based on a set of rules
    """

    def __init__(self, config, dir):
        self.config = config
        self.dir = dir

    def scan_dir(self):
        """
        Sanitises any applicable files in the directory based on rules defined
        :return: None
        """

        if not os.path.isdir(self.dir):
            print("Error: path does not exist")
            sys.exit(1)
        
        print("Scanning directory...")

        valid_files = []

        # determine which files will be sanitised based on file_extensions in config
        for root, subdirs, files in os.walk(self.dir):
            for name in files:
                if os.path.splitext(name)[1] in self.config['file_extensions']:
                    valid_files.append(os.path.join(root, name))
                else:
                    print("Skipped file:", os.path.join(root, name))
        
        # now apply rules to each valid file
        for rule in self.config['rules']:
            if "substitute" in rule.keys():
                self.apply_substitute_rule(valid_files, rule['substitute']['find'], rule['substitute']['replace'])

    def apply_substitute_rule(self, files_list, find, replace):
        """
        Searches all occurences of find string and replaces it to replace string
        :param files_list: List of files to apply rules
        :param find: Substring to find
        :param replace: Substring to replace find with
        :return: string
        """

        # allows iteratation over lines from multiple input streams/files
        for item in files_list:

            # need to treat compressed files differently
            if os.path.splitext(item)[1] == ".gz":
                tmpfile = item + ".tmp"
                os.rename(item, tmpfile)
                with gzip.open(tmpfile, 'rt') as srcfile, gzip.open(item, 'at') as destfile:
                    for line in srcfile.readlines():
                        destfile.write(line.replace(find, replace))
                os.remove(tmpfile)

            elif os.path.splitext(item)[1] == ".bz2":
                tmpfile = item + ".tmp"
                os.rename(item, tmpfile)
                with bz2.open(tmpfile, 'rt') as srcfile, bz2.open(item, 'at') as destfile:
                    for line in srcfile.readlines():
                        destfile.write(line.replace(find, replace))
                os.remove(tmpfile)

            # assuming uncompressed text files
            else:
                with fileinput.input(item, inplace=True) as file:
                    for line in file:
                        print(line.replace(find, replace), end='')


def valid_config(config):
    """
    Checks to see if the config yaml file used is valid
    :param config: Dict representation of config
    :return: bool
    """
    
    supported_options = [
        'file_extensions',
        'rules'
        ]
    
    supported_rules = [
        'substitute'
    ]

    for options in config:
        if options not in supported_options:
            return False
    
    for rule in config['rules']:
        for r in rule.keys():
            if r not in supported_rules:
                return False

    return True


def load_config(config_file):
    """
    Loads a YAML configuration file into a Dictionary
    :param config_file: Filename of the configuration file
    :return: Dict
    """

    # take into account that RHEL 7 still uses Python 2.7 by default
    try:
        if six.PY2:
            config = yaml.load(open(config_file))
        else:
            config = yaml.load(open(config_file), Loader=yaml.FullLoader)

    except IOError as e:
        print(("Error: {msg}".format(msg=e.message)))
        sys.exit(1)

    except (yaml.scanner.ScannerError, yaml.parser.ParserError):
        print(("Error: Invalid YAML for config file {c}".format(c=config_file)))
        sys.exit(1)

    if not valid_config(config):
        print("Error: Invalid configuration options defined!")
        sys.exit(1)
    
    return config


def parse_args():
    """
    Adds command line arguments to script
    :return: argparse.Namespace object
    """
    parser = ArgumentParser()

    parser.add_argument("-c", "--config", help="configuration file",
                        default="sample-config.yml")
    parser.add_argument("dir", nargs=1, help="directory to sanitise")

    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)

    sanitiser = Sanitiser(config, args.dir[0])
    sanitiser.scan_dir()


if __name__ == "__main__":
    main()
