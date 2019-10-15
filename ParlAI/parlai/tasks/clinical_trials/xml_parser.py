#### Globals/Imports ####

import json
import xml
import xmltodict
import xml.etree.ElementTree as ET
import os
import collections
from timeit import default_timer as timer
import datetime
import traceback
import sys
import re

#### Custom Exceptions ####

class ClinicalTrialParseException(Exception):
	pass

#### ProcessedClinicalTrial Class Definition ####

class ProcessedClinicalTrial:
	"""Wrapper class and methods for converting pubmed XML (as instance of ElementTree root)
	to JSON format for posting to elasticsearch.
	"""
	def __init__(self, ct_root):
		self.get_titles(ct_root)
		self.get_description_and_summary(ct_root)
		self.get_status(ct_root)
		self.get_date_info(ct_root)
		self.get_phase(ct_root)
		self.get_enrollment_info(ct_root)
		self.get_conditions(ct_root)
		self.get_intervention_info(ct_root)
		self.get_eligibility_info(ct_root)
		self.get_location_info(ct_root)
		self.get_keywords(ct_root)
		self.nct_id = ct_root.find("id_info").find("nct_id").text
		self.url = ct_root.find("required_header").find("url").text

	#### Clinical Trial XML Parsing Methods ####

	def get_description_and_summary(self, ct_root):
		self.detailed_description = ""
		self.brief_summary = ""
		detailed_description = ct_root.find("detailed_description")
		if (detailed_description is not None):
			textblock = detailed_description.find("textblock")
			if (textblock is not None):
				self.detailed_description = textblock.text
			else:
				self.detailed_description = detailed_description.text
		brief_summary = ct_root.find("brief_summary")
		if (brief_summary is not None):
			textblock = brief_summary.find("textblock")
			if (textblock is not None):
				self.brief_summary = textblock.text.replace('\n', ' ')
			else:
				self.brief_summary = brief_summary.text

	def get_conditions(self, ct_root):
		self.condition_info = {
			'conditions': [],
			'mesh_terms': []
		}
		# get conditions (found in <condition></condition> tags)
		conditions = ct_root.findall("condition")
		if (conditions is not None):
			self.condition_info['conditions'] = [c.text for c in conditions]
		# get condition mesh terms (found in <condition_browse></condition_browse> tags)
		condition_browse = ct_root.find('condition_browse')
		if (condition_browse is not None):
			mesh_terms = condition_browse.findall('mesh_term')
			if (mesh_terms is not None):
				self.condition_info['mesh_terms'] = [m.text for m in mesh_terms]

	def get_location_info(self, ct_root):
		self.location = {
			'facility': {
				'name': None,
				'address': {
					'city': None,
					'state': None,
					'zip': None,
					'country': None,
				},
			}
		}
		self.location_countries = []
		location = ct_root.find("location")
		if (location is not None):
			facility = location.find("facility")
			if (facility is not None):
				name = facility.find("name")
				if (name is not None):
					self.location['facility']['name'] = name.text
				address = facility.find('address')
				if (address is not None):
					city = address.find('city')
					if (city is not None):
						self.location['facility']['address']['city'] = city.text
					state = address.find('state')
					if (state is not None):
						self.location['facility']['address']['state'] = state.text
					zip = address.find('zip')
					if (zip is not None):
						self.location['facility']['address']['zip'] = zip.text
					country = address.find('country')
					if (country is not None):
						self.location['facility']['address']['country'] = country.text
		location_countries = ct_root.find('location_countries')
		if (location_countries is not None):
			self.location_countries = [c.text for c in location_countries]

	# todo: further parse the inclusion and exclusion criteria portions of criteria texblock
	def get_eligibility_info(self, ct_root):
		self.eligibility = {
			'inclusion_criteria': '',
			'exclusion_criteria': '',
			'gender': '',
			'minimum_age': '',
			'maximum_age': '',
			'healthy_volunteers': ''
		}
		eligibility = ct_root.find('eligibility')
		if (eligibility is not None):
			criteria = eligibility.find('criteria')
			if (criteria is not None):
				textblock = criteria.find('textblock')
				if (textblock is not None):
					# todo: parse this more to obtain lists of inclusion and exclusion criteria
					inclusion_criteria = ''
					exclusion_criteria = ''
					m1 = re.search('Inclusion Criteria:|Inclusion Criteria', textblock.text, re.IGNORECASE)
					m2 = re.search('Exclusion Criteria:|Exclusion Criteria', textblock.text, re.IGNORECASE)
					if (m1 is not None and m2 is not None):
						# inclusion and exclusion provided
						inclusion_index = m1.span(0)[1]
						exclusion_index = m2.span(0)[0]
						inclusion_criteria = textblock.text[inclusion_index:exclusion_index]
						exclusion_criteria = textblock.text[m2.span(0)[1]:]
					elif (m1 is not None):
						# only inclusion provided
						inclusion_index = m1.span(0)[1]
						inclusion_criteria = textblock.text[inclusion_index:]
					elif (m2 is not None):
						# only exclusion provided
						exclusion_index = m2.span(0)[1]
						exclusion_criteria = textblock.text[exclusion_index:]
					self.eligibility['inclusion_criteria'] = inclusion_criteria
					self.eligibility['exclusion_criteria'] = exclusion_criteria
			gender = eligibility.find('gender')
			if (gender is not None):
				self.eligibility['gender'] = gender.text
			minimum_age = eligibility.find('minimum_age')
			if (minimum_age is not None):
				self.eligibility['minimum_age'] = minimum_age.text
			maximum_age = eligibility.find('maximum_age')
			if (maximum_age is not None):
				self.eligibility['maximum_age'] = maximum_age.text
			healthy_volunteers = ct_root.find('healthy_volunteers')
			if (healthy_volunteers is not None):
				self.eligibility['healthy_volunteers'] = healthy_volunteers.text

	def get_intervention_info(self, ct_root):
		self.intervention_info = {
			'interventions': [],
			'mesh_terms': []
		}
		# parse intervention tags
		interventions = ct_root.findall('intervention')
		if (interventions is not None):
			for i in interventions:
				intervention = {'type': '', 'name': '', 'description': '', 'arm_group_label': ''}
				intervention_type = i.find("intervention_type")
				if (intervention_type is not None):
					intervention['type'] = intervention_type.text
				intervention_name = i.find('intervention_name')
				if (intervention_name is not None):
					intervention['name'] = intervention_name.text
				description = i.find('description')
				if (description is not None):
					intervention['description'] = description.text
				arm_group_label = i.find('arm_group_label')
				if (arm_group_label is not None):
					intervention['arm_group_label'] = arm_group_label.text
				self.intervention_info['interventions'].append(intervention)
		# get intervention mesh terms
		intervention_browse = ct_root.find('intervention_browse')
		if (intervention_browse is not None):
			mesh_terms = intervention_browse.findall('mesh_term')
			if (mesh_terms is not None):
				self.intervention_info['mesh_terms'] = [m.text for m in mesh_terms]


	def get_enrollment_info(self, ct_root):
		self.enrollment = {
			'type': 'Actual',
			'number': '0'
		}
		enrollment = ct_root.find('enrollment')
		if (enrollment is not None):
			if ('type' in enrollment.attrib):
				self.enrollment['type'] = enrollment.attrib['type']
			self.enrollment['number'] = enrollment.text

	def get_date_info(self, ct_root):
		self.dates = {
			'start_date': 'Unknown',
			'start_date_type': 'Actual',
			'completion_date': 'Unknown',
			'completion_date_type': 'Actual',
			'primary_completion_date': 'Unknown',
			'primary_completion_date_type': 'Actual',
		}
		start_date = ct_root.find('start_date')
		if (start_date is not None):
			if ('type' in start_date.attrib):
				self.dates['start_date_type'] = start_date.attrib['type']
			self.dates['start_date'] = start_date.text
		completion_date = ct_root.find('completion_date')
		if (completion_date is not None):
			if ('type' in completion_date.attrib):
				self.dates['completion_date_type'] = completion_date.attrib['type']
			self.dates['completion_date'] = completion_date.text
		primary_completion_date = ct_root.find('primary_completion_date')
		if (primary_completion_date is not None):
			if ('type' in primary_completion_date.attrib):
				self.dates['primary_completion_date_type'] = primary_completion_date.attrib['type']
			self.dates['primary_completion_date'] = primary_completion_date.text

	def get_phase(self, ct_root):
		self.phase = 'Unknown'
		phase = ct_root.find('phase')
		if (phase is not None):
			self.phase = phase.text

	def get_titles(self, ct_root):
		self.brief_title = ''
		self.official_title = ''
		brief_title = ct_root.find("brief_title")
		if (brief_title is not None):
			self.brief_title = brief_title.text
		official_title = ct_root.find("official_title")
		if (official_title is not None):
			self.official_title = official_title.text

	def get_status(self, ct_root):
		self.overall_status = 'Unknown'
		overall_status = ct_root.find("overall_status")
		if (overall_status is not None):
			self.overall_status = overall_status.text

	def get_mesh_terms(self, ct_root):
		# get mesh terms for the CT's intervention
		self.intervention_mesh_terms = []
		intervention_browse = []
		# get mesh terms for the condition under investigation
		self.condition_mesh_terms = []


	def get_keywords(self, ct_root):
		self.keywords = []
		keywords = ct_root.findall('keyword')
		if (keywords is not None):
			self.keywords = [k.text for k in keywords]

	#### Utilities ####
	def to_json(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)