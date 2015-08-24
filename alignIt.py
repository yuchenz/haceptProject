#!/usr/bin/python2.7

import argparse
import os, sys, pdb
import codecs
from subtreeAlign import align, topAlign
from sntAlign import sntAlign
from evalSubtreeAlignment import evaluate
from Bead import Bead

debug_log = sys.stderr
out = sys.stdout

def main():
	arg_parser = argparse.ArgumentParser(description="Subtree Aligner")

	arg_parser.add_argument('-t', '--test_data', help='the directory of the gold data to be subtree aligned for evaluation')
	arg_parser.add_argument('-d', '--temp_dir', help='directory for storing temporary files and experimental output files')
	arg_parser.add_argument('-w', '--wa_file', help='filename of the word alignment file (should be stored in temp_dir)')
	arg_parser.add_argument('-a', '--analysis', help='flag to enable output for analysis, and the directory to store the output files')

	args = arg_parser.parse_args()

	# files that need to be prepared in ahead
	compiled_data = 'hacept'
	lan1_suffix = '.ch'
	lan2_suffix = '.en'
	bps_suffix = '.preprocessed.bps'
	
	wa_file = args.wa_file 
	temp_dir_files = os.listdir(args.temp_dir)
	auto_subtree_suffix = '.subtree.auto'
	analysis_file = 'analysis'

	# step 1: compile data
	assert compiled_data + lan1_suffix in temp_dir_files and compiled_data + lan2_suffix in temp_dir_files, \
			'File Not Found: compiled sentences data not ready!'
	print >> out, 'compiled sentences data ready!'

	# step 2: preprocessing & word alignment
	assert wa_file in temp_dir_files, 'File Not Found: word alignment file not ready!'
	print >> out, 'word alignment file ready!'

	# step 3: parsing using Berkeley Parser
	assert compiled_data + lan1_suffix + bps_suffix in temp_dir_files and \
			compiled_data + lan2_suffix + bps_suffix in temp_dir_files, \
			'File Not Found: berkeley parsed files not ready!'
	print >> out, 'berkeley parsed files ready!'

	# step 4: subtree alignment w/ frame extraction
	print >> out, 'subtree alignment w/ frame extraction ...'
	sntFrameList = align(os.path.join(args.temp_dir, compiled_data + lan1_suffix + bps_suffix), 
			os.path.join(args.temp_dir, compiled_data + lan2_suffix + bps_suffix),
			os.path.join(args.temp_dir, wa_file)) 

	# step 5: subtree alignment evaluation w/ sentence align
	print >> out, 'subtree alignment evaluation w/ sentence align ...'
	sntList = [line.split() for line in codecs.open(os.path.join(args.temp_dir, compiled_data + lan2_suffix), 'r', 'utf-8').readlines()]
	alignedSntFrameList = sntAlign(sntFrameList, sntList)

	print >> out, 'reading in all beads ...'
	beadList = []
	for filename in os.listdir(args.test_data):
		print filename,
		beadList.extend(Bead.loadData(os.path.join(args.test_data, filename)))
		
	evaluate(beadList, alignedSntFrameList)

	# output for analysis
	if args.analysis:
		print >> out, 'outputing for analysis ...'
		outf1 = codecs.open(os.path.join(args.analysis, analysis_file+'.gold'), 'w', 'utf-8')
		outf2 = codecs.open(os.path.join(args.analysis, analysis_file+'.auto'), 'w', 'utf-8')
		for i, bead in enumerate(beadList):
			sntFrame = alignedSntFrameList[i]
			tmp = '='*30+'snt'+str(i)+'='*30
			tmp = tmp.encode('utf-8')
			print >> outf1, tmp
			print >> outf1, bead.__str__().decode('utf-8')
			print >> outf1, '\n\n'
			print >> outf2, tmp
			print >> outf2, sntFrame.__str__().decode('utf-8')
			print >> outf2, '\n\n'
		outf1.close()
		outf2.close()


if __name__ == '__main__':
	main()
