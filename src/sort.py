"""
This script will query for an analysis from OneCodex,
download the readlevel species assignment and sort 
the sequence into files based on this assignment. 
"""

import requests
import json
from Bio import SeqIO
import csv
from collections import Counter
import os
from os.path import join as join_path
ONECODEX_API_KEY = "f89f973f60c74b7e8848342f5c663378"
ONECODEX_API_PWD = ""

def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]     


class FastqSorter(object):

    def __init__(self, fasta_file_path,readlevel_assignment_tsv_file_path, analysis_id = ""):
        self.fasta_file_path = fasta_file_path
        self.readlevel_assignment_tsv_file_path = readlevel_assignment_tsv_file_path
        self.assignment_dic = {}
        self.get_assignment_dic()
        self.records_by_species= {}
        self.taxon_id_to_species = self.get_taxon_to_species_dict()
        self.analysis_id = analysis_id
        self.out_dir = join_path(_APP.config['UPLOAD_FOLDER'],self.analysis_id)
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    def sort(self):
        self.sort_reads_by_species()
        self.write_sorted_files()


    def get_assignment_dic(self):
        self.assignment_dic = {}
        with open(self.readlevel_assignment_tsv_file_path,'r') as infile:
            reader = csv.reader(infile,delimiter= "\t")
            for row in reader:
                read_id = row[0].replace('@','')
                taxon_id = row[1]
                self.assignment_dic[read_id] = taxon_id

    def sort_reads_by_species(self):
        for i,record in enumerate(SeqIO.parse(self.fasta_file_path, "fastq")):
            species = self.taxon_id_to_species[self.assignment_dic[record.id]]['name']
            try:
                self.records_by_species[species].append(record)
            except KeyError:
                self.records_by_species[species] = [record]

    def write_sorted_files(self):
        for species,record_list in self.records_by_species.iteritems():
            filename = species.replace(' ','_').replace('/','_')+".fastq"
            with open(join_path(self.out_dir,filename),'w') as outfile:
                SeqIO.write(record_list, outfile, "fastq")

    def get_all_species_present(self):
        return unique(self.assignment_dic.values())

    def count_read_assignment(self):
        return Counter(self.assignment_dic.values())

    def get_taxon_to_species_dict(self):
        with open('taxonomy_metadata.json','r') as infile:
            return json.load(infile)



# sorter = FastqSorter("/Users/phelimb/Dropbox/Mykrobe_test_samples/SampleName_S1_L001_R1_001.fastq","SampleName_S1_L001_R1_001.fastq.gz.results.tsv")
# sorter.sort()
