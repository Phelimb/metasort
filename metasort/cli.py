#! /usr/bin/env python
"""A command line interface for sorting metagenomic sequence data using the onecodex API"""

import argparse
import sys
import os
from os.path import join as join_path

import logging
logging.basicConfig(level=logging.WARNING)

from utils import is_allowed_file
from utils import upload_genome_file_path
from utils import get_analyses
from utils import get_analysis_from_id
from utils import process_analysis
from sort import FastqSorter
from time import sleep
from utils import get_taxon_to_species_dict

parser = argparse.ArgumentParser(description='Sort sequence data by species using OneCodex')
parser.add_argument('file', metavar='f', type=str,  help='path to a fasta or fastq file')
parser.add_argument('outdir',type=str,  help='output directory', default=None, nargs='?')



class Cli(object):

	def __init__(self, args):
		self.file = args.file 
		self.outdir = args.outdir
		self._check_inputs()
		self._change_file_ext_to_long()
		self.sample_id = ""
		self.analysis_id = ""

	def _check_inputs(self):
		if self.file is None:
			print parser.print_help()
			sys.exit()
		if not is_allowed_file(self.file):
			print "Unzipped fastq or fasta files with ext fa,fq,fasta,fastq"
			sys.exit()

	def run(self):
		self._upload_genome_file_path()
		self._get_analysis_id()
		self._make_out_dir()
		self._wait_for_results_to_proccess()
		self._process_analysis()
		self._sort_sequence()
		print self.outdir

	def _change_file_ext_to_long(self):
	    ext = self.file.rsplit('.', 1)[1]
	    if ext == "fq":
	        self.file = self.file.replace("fq","fastq")
	    elif ext == "fa":
	        self.file =self.file.replace("fa","fasta")

	def _upload_genome_file_path(self):
		self.sample_id = upload_genome_file_path(self.file)
		logging.info("sample_id: %s" % self.sample_id) 

	def _get_analysis_id(self):
		analyses = get_analyses()
		for a in analyses:
			if a['sample_id'] == self.sample_id and a['reference_name'] == "One Codex Database":
				self.analysis_id = a['id']
		logging.info("analysis_id: %s" % self.analysis_id) 

	def _make_out_dir(self):
		if not self.outdir:
			self.outdir = self.analysis_id
		if not os.path.exists(self.outdir):
			os.makedirs(self.outdir)

	def _wait_for_results_to_proccess(self):
		process_complete = False
		logging.info("Starting analysis")
		while not process_complete:
			analysis = get_analysis_from_id(self.analysis_id)
			if analysis['analysis_status'] != "Pending":
				process_complete = True
			else:
				logging.info(analysis['analysis_status'])
				sleep(30)
		logging.info("Ending analysis")

	def _process_analysis(self):
		process_analysis(self.analysis_id, dir = self.outdir)

	def _sort_sequence(self):
		readlevel_assignment_tsv_file_path = join_path(self.outdir,"read_data_" + self.analysis_id + '.tsv')           
		sorter = FastqSorter(self.file,readlevel_assignment_tsv_file_path)
		sorter.sort()	
		sorter.write_sorted_files(self.outdir, taxon_id_to_species_name = get_taxon_to_species_dict() )

def main():
	args = parser.parse_args()
	cli = Cli(args)
	cli.run()

if __name__ == "__main__":
    main()

