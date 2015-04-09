#! /usr/bin/env python
"""A command line interface for sorting metagenomic sequence data using the onecodex API"""

import argparse

parser = argparse.ArgumentParser(description='Sort sequence data by species using OneCodex')
parser.add_argument('file', metavar='f', type=str,  help='path to a fasta or fastq file')
parser.add_argument('-o','--outdir',type=str,  help='output directory')
args = parser.parse_args()

print args.file
print args.outdir

