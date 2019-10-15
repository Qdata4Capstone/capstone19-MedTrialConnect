from .data_process import json2txt, xml2json

import parlai.core.build_data as build_data
import os

"""
Data files definitions
"""
TASK_DIR = 'clinical_trials' 
XML_DIR = 'xml'
JSON_DIR = 'json'
TXT_DIR = 'txt'
TXT_FILE = 'all_trials.txt'


def build(opt):
    task_path = os.path.join(opt['datapath'], TASK_DIR)
    xml_dir_path = os.path.join(task_path, XML_DIR)
    json_dir_path = os.path.join(task_path, JSON_DIR)
    txt_dir_path = os.path.join(task_path, TXT_DIR)
    txt_file_path = os.path.join(txt_dir_path, TXT_FILE)
    version = None
    if not build_data.built(task_path, version_string=version):
        print('[building data: ' + task_path + ']')
        # make a clean directory if needed
        if build_data.built(task_path):
            # an older version exists, so remove these outdated files.
            build_data.remove_dir(task_path)
        build_data.make_dir(task_path)
        build_data.make_dir(xml_dir_path)
        build_data.make_dir(json_dir_path)
        build_data.make_dir(txt_dir_path)
        # download data
        fname = "AllPublicXML.zip"
        url = "https://clinicaltrials.gov/"+fname
        build_data.download(url, xml_dir_path, fname, True)
        # build and process data
        build_data.unzip(xml_dir_path, fname)
        xml2json(xml_dir_path, json_dir_path)
        json2txt(json_dir_path, txt_file_path)
        # mark the data as built
        build_data.mark_done(task_path, version_string=version)