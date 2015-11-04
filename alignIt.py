#!/usr/bin/python2.7 

import argparse
import os, sys, pdb
import codecs
from subtreeAlign import align, topAlign
from sntAlign import sntAlign
from evalSubtreeAlignment import evaluate
from Bead import Bead
import time

debug_log = sys.stderr
out = sys.stdout

def main():
	arg_parser = argparse.ArgumentParser(description="Subtree Aligner")

	arg_parser.add_argument('-t', '--test_data', help='the directory of the gold data to be subtree aligned for evaluation')
	arg_parser.add_argument('-d', '--temp_dir', help='directory for storing temporary files and experimental output files')
	arg_parser.add_argument('-w', '--wa_file', help='filename of the word alignment file (should be stored in temp_dir)')
	arg_parser.add_argument('-a', '--analysis', help='flag to enable output for analysis, and the directory to store the output files')

	arg_parser.add_argument('--stem', help='stem filename of the data', default='hacept100')
	arg_parser.add_argument('--fsuffix', help='foreign file suffix', default='ch')
	arg_parser.add_argument('--esuffix', help='english file suffix', default='en')
	arg_parser.add_argument('--psuffix', help='parse file suffix', default='bps')
	arg_parser.add_argument('--ssuffix', help='subtree alignment file suffix', default='suba')

	arg_parser.add_argument('--align_func', help='subtree alignment function', default='bottom')
	arg_parser.add_argument('--num_proc', type=int, help='number of parallel processes', default=24)

	arg_parser.add_argument('--soft_eval', action='store_true', help='evaluation: if any frame contains a gold subtree alignment, \
			count it as one correct alignment point', default=False)

	arg_parser.add_argument('--ex', action='store_true', help='turn on rule extraction', default=False)
	arg_parser.add_argument('--wordRulesFlag', action='store_true', help='turn on word level rule extraction, \
			i.e. add word alignments that are not in subtree alignments to the rule table', default=False)
	arg_parser.add_argument('--evalFlag', action='store_true', help='turn on subtree alignment evaluation', default=False)
	arg_parser.add_argument('--minMemFlag', action='store_true', help='turn on minimizing memory use \
			(in this mode, only rule extraction can be done, no subtree alignment evaluation)', default=False)

	args = arg_parser.parse_args()

	# files that need to be prepared in ahead
	compiled_data = args.stem
	lan1_suffix = '.' + args.fsuffix
	lan2_suffix = '.' + args.esuffix
	bps_suffix = '.' + args.psuffix
	suba_suffix = '.' + args.ssuffix
	
	wa_file = args.wa_file 
	temp_dir_files = os.listdir(args.temp_dir)
	analysis_file = 'analysis'

	# step 1: compile data
	assert compiled_data + lan1_suffix in temp_dir_files and compiled_data + lan2_suffix in temp_dir_files, \
			'File Not Found: compiled sentences files not ready! %s %s' % (compiled_data + lan1_suffix, compiled_data + lan2_suffix)
	print >> out, 'compiled sentences files ready!', compiled_data + lan1_suffix, compiled_data + lan2_suffix

	# step 2: preprocessing & word alignment
	assert wa_file in temp_dir_files, 'File Not Found: word alignment file not ready! %s' % wa_file
	print >> out, 'word alignment file ready!', wa_file

	# step 3: parsing using Berkeley Parser
	assert compiled_data + lan1_suffix + bps_suffix in temp_dir_files and \
			compiled_data + lan2_suffix + bps_suffix in temp_dir_files, \
			'File Not Found: parsed files not ready! %s %s' % \
			(compiled_data + lan1_suffix + bps_suffix, compiled_data + lan2_suffix + bps_suffix)
	print >> out, 'parsed files ready!', compiled_data + lan1_suffix + bps_suffix, compiled_data + lan2_suffix + bps_suffix 

	# step 4: subtree alignment w/ frame extraction & rule extraction if turned on
	print >> out, 'subtree alignment w/ frame extraction ...'
	s = time.time()
	sntFrameList = align(os.path.join(args.temp_dir, compiled_data + lan1_suffix + bps_suffix), 
			os.path.join(args.temp_dir, compiled_data + lan2_suffix + bps_suffix),
			os.path.join(args.temp_dir, wa_file), args.align_func, args.num_proc, args.ex, args.wordRulesFlag, args.minMemFlag)
	print >> out, 'sntFrameList size: ', len(sntFrameList)
	print >> out, 'subtree alignment time: ', time.time() - s, 's'

	# [old version] step 5: subtree alignment evaluation w/ sentence align
	#print >> out, 'subtree alignment evaluation w/ sentence align ...'
	#sntList = [line.split() for line in codecs.open(os.path.join(args.temp_dir, compiled_data + lan2_suffix), 'r', 'utf-8').readlines()]
	#print >> out, 'sntList size: ', len(sntList)
	#alignedSntFrameList = sntAlign(sntFrameList, sntList)
	#print >> out, 'alignedSntFrameList size: ', len(alignedSntFrameList)

	# [new version] step 5: subtree alignment evaluation w/ sentence align
	alignedSntFrameList = sntFrameList

	if args.evalFlag and not args.minMemFlag:
		evaluate(os.path.join(args.temp_dir, compiled_data + suba_suffix), alignedSntFrameList, args.soft_eval, args.analysis)

	# if rule extraction
	if args.ex:
		print >> out, 'outputing extracted rules in moses format ...'
		s = time.time()
		ans, ans1 = [], []
		for sntFrame in alignedSntFrameList:
			#pdb.set_trace()
			if sntFrame == None:
				continue
			# put extracted rules into rule files
			for rule in sntFrame.ruleList:
				ruleNInv, ruleInv = rule.mosesFormatRule()
				ans.append(ruleNInv)
				ans1.append(ruleInv)

		ans.sort(); ans1.sort()
		print >> out, 'sorting rules / inversed rules time: ', time.time() - s, 's'
		s = time.time()
		outf = codecs.open(os.path.join('/dev/shm/', args.stem+'.exRules'), 'w', 'utf-8')
		outf1 = codecs.open(os.path.join('/dev/shm/', args.stem+'.inv.exRules'), 'w', 'utf-8')
		#outf = codecs.open(os.path.join(args.temp_dir, args.stem+'.exRules'), 'w', 'utf-8')
		#outf1 = codecs.open(os.path.join(args.temp_dir, args.stem+'.inv.exRules'), 'w', 'utf-8')
		for a in ans: outf.write(a)
		for a in ans1: outf1.write(a)
		outf.close(); outf1.close()
		print >> out, 'output all rules time: ', time.time() - s, 's'

	# if output for analysis
	if args.analysis:
		beadList = []
		for filename in os.listdir(args.test_data):
			print filename,
			beadList.extend(Bead.loadData(os.path.join(args.test_data, filename)))

		print >> out, '\noutputing auto and gold files for analysis ...'
		outf1 = codecs.open(os.path.join(args.analysis, analysis_file+'.gold'), 'w', 'utf-8')
		outf2 = codecs.open(os.path.join(args.analysis, analysis_file+'.auto'), 'w', 'utf-8')
		k = 0
		for i, bead in enumerate(beadList):
			if k >= len(alignedSntFrameList):
				break
			#print k, len(alignedSntFrameList)
			sntFrame = alignedSntFrameList[k]
			if ''.join(sntFrame.tgtWordList).lower() != ''.join(bead.tgtSnt).lower():
				continue
			tmp = '='*30+'snt'+str(k)+'='*30
			tmp = tmp.encode('utf-8')
			print >> outf1, tmp
			print >> outf1, bead.__str__().decode('utf-8')
			print >> outf1, '\n\n'

			print >> outf2, tmp
			print >> outf2, sntFrame.__str__().decode('utf-8')
			print >> outf2, '\n\n'

			k += 1

		outf1.close(); outf2.close()

if __name__ == '__main__':
	main()
