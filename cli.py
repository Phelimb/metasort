#! /usr/bin/env python
"""A command line interface for sorting metagenomic sequence data using the onecodex API"""

import argparse
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from metasort import upload_genome_file_path
from metasort import get_analyses
from metasort import get_analysis_from_id
from metasort import process_analysis

from time import sleep

parser = argparse.ArgumentParser(description='Sort sequence data by species using OneCodex')
parser.add_argument('file', metavar='f', type=str,  help='path to a fasta or fastq file')
parser.add_argument('outdir',type=str,  help='output directory', default=None, nargs='?')
args = parser.parse_args()


class Cli(object):

	def __init__(self, args):
		self.file = args.file 
		self.outdir = args.outdir
		self._check_inputs()
		self.sample_id = ""
		self.analysis_id = ""

	def _check_inputs(self):
		if self.file is None:
			print parser.print_help()
			sys.exit()		

	def run(self):
		self._upload_genome_file_path()
		self._get_analysis_id()
		self._wait_for_results_to_proccess()
		self._process_analysis()

	def _upload_genome_file_path(self):
		self.sample_id = upload_genome_file_path(self.file)
		logging.info("sample_id: %s" % self.sample_id) 

	def _get_analysis_id(self):
		analyses = get_analyses()
		for a in analyses:
			if a['sample_id'] == self.sample_id and a['reference_name'] == "One Codex Database":
				self.analysis_id = a['id']
		logging.info("analysis_id: %s" % self.analysis_id) 

	def _wait_for_results_to_proccess(self):
		process_complete = False
		logging.info("Starting analysis")
		while not process_complete:
			analysis = get_analysis_from_id(self.analysis_id)
			if analysis['analysis_status'] == "Success":
				process_complete = True
			else:
				sleep(5)
		logging.info("Ending analysis")

	def _process_analysis(self):
		process_analysis(self.analysis_id)








cli = Cli(args)
cli.run()

