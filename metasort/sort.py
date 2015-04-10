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


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]     


class FastqSorter(object):

    def __init__(self, fasta_file_path,readlevel_assignment_tsv_file_path):
        self.fasta_file_path = fasta_file_path
        self.readlevel_assignment_tsv_file_path = readlevel_assignment_tsv_file_path
        self.assignment_dic = {}
        self.get_assignment_dic()
        self.records_by_tax_id= {}
        self.ext = self.fasta_file_path.rsplit('.', 1)[1]
        self.long_ext = self.ext
        self._change_file_ext_to_long()

    def _change_file_ext_to_long(self):
        if self.long_ext == "fq":
            self.long_ext = "fastq"
        elif self.long_ext == "fa":
            self.long_ext = "fasta"

    def sort(self):
        self.sort_reads_by_taxon_id()

    def get_assignment_dic(self):
        self.assignment_dic = {}
        with open(self.readlevel_assignment_tsv_file_path,'r') as infile:
            reader = csv.reader(infile,delimiter= "\t")
            for row in reader:
                read_id = row[0].replace('@','').replace(">","")
                taxon_id = row[1]

                self.assignment_dic[read_id] = taxon_id

    def sort_reads_by_taxon_id(self):
        for i,record in enumerate(SeqIO.parse(self.fasta_file_path, self.long_ext)):
            taxon_id = self.assignment_dic[record.description]
            try:
                self.records_by_tax_id[taxon_id].append(record)
            except KeyError:
                self.records_by_tax_id[taxon_id] = [record]

    def write_sorted_files(self,out_dir, taxon_id_to_species_name = {}):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for taxon_id,record_list in self.records_by_tax_id.iteritems():
            fileprefix = taxon_id_to_species_name.get(taxon_id,taxon_id)
            if fileprefix == "null":
                fileprefix = "unknown"
            filename = ".".join([fileprefix , self.ext])
            with open(join_path(out_dir,filename),'w') as outfile:
                SeqIO.write(record_list, outfile, self.long_ext)

    def get_all_species_present(self):
        return unique(self.assignment_dic.values())

    def count_read_assignment(self):
        return Counter(self.assignment_dic.values())

