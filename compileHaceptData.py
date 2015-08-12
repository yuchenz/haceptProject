#!/usr/bin/python2.7

import sys
import os
import codecs
from Bead import Bead

def compileData(dirname, output):
	"""
	Compile hacept raw data in separated files in hacept_raw_data into hacept.ch and hacept.en in hacept_compiled_data,
	containing word separated sentences only.

	:type dirname: str
	:param dirname: the directory that contains the hacept raw data

	:type output: str
	:param output: the output file stem, i.e. the source language output file is "output".ch and target language is "output".en

	"""
	chF = codecs.open(output+'.ch', 'w', 'utf-8')
	enF = codecs.open(output+'.en', 'w', 'utf-8')
	for filename in os.listdir(dirname):
		print os.path.join(dirname, filename)
		beadList = Bead.loadData(os.path.join(dirname, filename))
		for bead in beadList:
			chF.write(' '.join(bead.srcTree.leaves())+'\n')
			enF.write(' '.join(bead.tgtTree.leaves())+'\n')
	chF.close()
	enF.close()

if __name__ == "__main__":
	compileData(sys.argv[1], sys.argv[2])
