from .xml_parser import ClinicalTrialParseException, ProcessedClinicalTrial
from timeit import default_timer as timer

import os
import sys
import json
import string
import datetime
import unicodedata
import traceback
import xml.etree.ElementTree as ET


"""
Extract all fields from nested clinical trial data structure
"""
def extract_fields(trial_data):
    fields = []
    if isinstance(trial_data, dict):
        for _, value in trial_data.items():
            if isinstance(value, str):
                fields.append(value)
            else:
                fields.extend(extract_fields(value))
    elif isinstance(trial_data, list):
        for value in trial_data:
            if isinstance(value, str):
                fields.append(value)
            else:
                fields.extend(extract_fields(value))
    return fields


'''
* After downloaded from clinicaltrials.gov and extracted, file structure should look like:
	AllPublicXML/ 
		NCT0000xxxx/
			Files: NCT00000000.xml - NCT00009997.xml
			(around 5-10,000 trials per folder and just 1 clinical trial XML tree per file)
		...
		NCT0362xxxx/
			NCT03620006.xml, etc
	If subdirectories aren't there (i.e., AllPublicXML directly contains XML files), that should be fine too.
* This methods reads and parses all of the CT XML files it can find and converts them
	to a JSON format ready to be posted to elasticsearch via the elasticsearch bulk_add API.
* API endpoint is /_bulk and it expcts JSON files with repeating lines of the following format:
	action_and_meta_data\n
	optional_source\n
* Each JSON file to post via bulk_add should have <= 5000 records
'''
def xml2json(xml_dir, json_dir):
	if not os.path.exists(json_dir):
		os.makedirs(json_dir)
	json_file_base = os.path.join(json_dir, 'data_')
	json_file_num = 0
	count = 0
	metdata = {"index": {"_index": "clinicaltrials", "_type":"trial", "_id": count}}

	print("Converting XML to JSON")
	print("Estimating time remaining...")
	start = timer()
	json_lines_to_write = []
	num_errors = 0

	for root, dirs, files in os.walk(xml_dir):
		for file in files:
			try:
				if (file.endswith('.xml')):
					# parse XML file to XML tree
					xml_file = os.path.join(root, file)
					ct_root = ET.parse(xml_file).getroot()
					
					# convert into JSON for posting to elasticsearch
					processed_ct = ProcessedClinicalTrial(ct_root)
					count += 1
					metdata['index']['_id'] = processed_ct.nct_id
					
					# update array containing lines for elasticsearch
					json_lines_to_write.append(json.dumps(metdata))
					json_lines_to_write.append(processed_ct.to_json())
					# estimate time remaining
					if (count == 200):
						end1 = timer()
						seconds_so_far = end1 - start
						minutes_remaining = int((float(seconds_so_far)/60)*(280000/count))
						print("Approximately " + str(minutes_remaining) + " minutes_remaining")
					
					# create a new json file for elasticsearch post every 5000 records
					if (count % 5000 == 0):
						print(str(count) + " docs processed...")
						json_file_num += 1
						json_file_name = json_file_base + str(json_file_num) + '.json'
						with open(json_file_name, 'w+') as f:
							for line in json_lines_to_write:
								f.write(line + '\n')
						json_lines_to_write = []

			except Exception:
				print("An error was encountered; check error_log.txt")
				num_errors += 1
				with open('error_log.txt', 'a+') as f:
					f.write(str(datetime.datetime.now()) + '\n')
					f.write("Error processing file " + file + '\n')
					traceback.print_exc(file=f)
				exit()

	# handle remaining records (for counts greater than last multiple of 5000)
	json_file_num += 1
	json_file_name = json_file_base + str(json_file_num) + '.json'
	with open(json_file_name, 'w+') as f:
		for line in json_lines_to_write:
			f.write(line + '\n')

	end2 = timer()
	print("Finished converting CT XML to JSON")
	seconds = end2 - start
	minutes = int(seconds/60)
	print("Stats: \n\tTotal time: " + str(minutes) + ' minutes' + '\n\tTrials processed: ' + str(count) + '\n\tErrors: ' + str(num_errors))


def json2txt(json_dir, txt_filename):
    # read all trials
    all_trials = []
    for root, dirs, files in os.walk(json_dir):
        for fname in files:
            try:
                if fname.endswith('.json'):
                    fpath = os.path.join(json_dir, fname)
                    with open(fpath) as f:
                        data = f.readlines()
                        for i in range(0, len(data), 2):
                            """
                            Each clinical trial data has two lines:
                            First line is the trial id
                            Second line is all the information about the trial such as summary, description...
                            """
                            trial_index = json.loads(data[i])['index'] 
                            trial_data = json.loads(data[i+1])
                            trial_data.update(trial_index)
                            all_trials.append(trial_data)

            except Exception:
                print("An error was encountered; check error_log.txt")
                num_errors += 1
                with open('error_log.txt', 'a+') as f:
                    f.write(str(datetime.datetime.now()) + '\n')
                    f.write("Error processing file " + fname + '\n')
                    traceback.print_exc(file=f)
                    exit()
    # process trials data and write all to file
    with open(txt_filename, 'w') as f:
		# punctuation removal
        tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))
        for trial_data in all_trials:
            trial_str = ' '.join(extract_fields(trial_data))
            # lowercase
            trial_str = trial_str.lower()
            # remove punctuation
            trial_str = trial_str.translate(tbl)
            # normalize whitespace
            trial_str = ' '.join(trial_str.split()) + '\n'
            f.write(trial_str)