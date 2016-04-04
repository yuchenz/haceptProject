#!/usr/bin/python2.7

import nltk
import sys
import pdb
import time
from util import extractAllSuba, cleanData

class Bead2:
	def __init__(self, srcTree, tgtTree, wordAlignment, goldSubtreeAlignment):
		"""
		Initialize a Bead instance.
		
		:type srcTree: nltk.ParentedTree
		:param srcTree: constitutent phrased-based (gold or parsed) tree on the source language (e.g. ch);

		:type srcTree: nltk.ParentedTree
		:param srcTree: constitutent phrased-based (gold or parsed) tree on the target language (e.g. en);

		:type wordAlignment: a list of lists
		:param wordAlignment: alignment between words, i.e. a matrix A,
								where A[i][j] == 1 indicates source word i is aligned with target word j; 

		:type subtreeAlignment: a list of lists, which contain 4-tuples
		:param subtreeAlignment: each element list is a frame,
								 each tuple (x1, y1, x2, y2) represents the subtree square on the word alignment matrix.
		"""
		self.srcTree = srcTree
		self.srcSnt = [word.lower() for word in srcTree.leaves()]
		self.tgtTree = tgtTree
		self.tgtSnt = [word.lower() for word in tgtTree.leaves()]
		self.wordAlignment = wordAlignment
		#s = time.clock()
		self.allSuba = extractAllSuba(srcTree, tgtTree, wordAlignment)
		#print >> sys.stderr, 'extract all suba: ', time.clock() - s
		# split out subtree alignments that are consistent with the word alignment, but are not in the gold suba list
		#s = time.clock()
		#pdb.set_trace()
		self.goldSuba, self.otherSuba = self.splitSuba(goldSubtreeAlignment)
		#print >> sys.stderr, 'split suba: ', time.clock() - s

	@classmethod
	def loadData(cls, filename):
		"""
		Return a list of Bead instances.
		Load trees, word alignments, and subtree alignments from a file, and create Bead instances. 

		:type filename: str
		:param filename: a file with trees, word alignments, and subtree alignments for multiple sentence pairs.

		"""
		import codecs
		f = codecs.open(filename, 'r', 'utf-8')
		blocks = cleanData(f.read()).split('\n\n')
		#blocks = f.read().split('\n\n')
		f.close()

		beadList = []

		srcTree = None
		tgtTree = None
		wordAlignment = None 
		subtreeAlignment = [] 

		for block in blocks[:-1]:
			s = time.clock()
			block = block.split('\n')
			i = 0
			errFlag = False
			while i < len(block):
				line = block[i]
				if line.startswith('SOURCE'):
					#print line
					if line[8:].startswith('ERROR'):
						errFlag = True
						break
					srcTree = nltk.ParentedTree(line[8:])
					if srcTree.leaves() == []:
						errFlag = True
						break
					#print srcTree.leaves()
					i += 1
					continue

				elif line.startswith('TARGET'):
					#print line
					tgtTree = nltk.ParentedTree(line[8:])
					#print tgtTree
					#print tgtTree.leaves()
					if tgtTree.leaves() == []:
						errFlag = True
						break
					wordAlignment = [[0 for j in xrange(len(tgtTree.leaves()))] for k in xrange(len(srcTree.leaves()))]
					i += 1
					#print i
					continue

				elif line.startswith('<mapping>'):
					#print "in mapping..."
					i += 1
					line = block[i]
					#print
					#print ' '.join([item.encode('utf-8') for item in srcTree.leaves()])
					#print
					#print srcTree
					#print srcSubtreeIndex
					#print
					#print tgtTree
					#print tgtSubtreeIndex
					while not line.startswith('</mapping>'):
						x1 = int(line.split()[0].split(',')[0])-1 
						x2 = int(line.split()[0].split(',')[-1])

						y1 = int(line.split()[1].split(',')[0])-1 
						y2 = int(line.split()[1].split(',')[-1])

						subtreeAlignment.append((x1, y1, x2, y2))
						i += 1
						line = block[i]

					i += 1
					continue

				elif line.startswith('<alignment>'):
					i += 1
					line = block[i]
					#print len(wordAlignment), len(wordAlignment[0])
					while not line.startswith('</alignment>'):
						#print line
						srcIndexes = [int(item)-1 for item in line.split()[0].split(',') if int(item) != -1]
						tgtIndexes = [int(item)-1 for item in line.split()[1].split(',') if int(item) != -1]
						for srcIndex in srcIndexes:
							for tgtIndex in tgtIndexes:
								wordAlignment[srcIndex][tgtIndex] = 1
						i += 1
						line = block[i]

					i += 1
					continue

				elif line.startswith('</bead>'):
					break
				
				i += 1
					
			#print >> sys.stderr, 'load block: ', time.clock() - s
			if not errFlag:
				beadList.append(cls(srcTree, tgtTree, wordAlignment, subtreeAlignment))
			srcTree, tgtTree, wordAlignment, subtreeAlignment = None, None, None, []

		return beadList
	
	def __str__(self):
		tmp = ''
		# src tree
		tmp += self.srcTree.pprint().encode('utf-8')+"\n\n"
		# tgt tree
		tmp += self.tgtTree.pprint().encode('utf-8')+"\n\n"
		# word alignment matrix
		for i in xrange(len(self.wordAlignment)):
			for j in xrange(len(self.wordAlignment[i])):
				tmp += str(self.wordAlignment[i][j])+' '
			tmp += '\n'
		tmp += '\n'
		# all subtree alignments
		tmp += str(len(self.allSuba)) + ' all subtree alignments:\n'
		for sbtrA in self.allSuba:
			tmp += sbtrA.__str__() + '\n'
		tmp += '\n'
		# gold subtree alignments
		tmp += str(len(self.goldSuba)) + ' gold subtree alignments:\n'
		for sbtrA in self.goldSuba:
			tmp += sbtrA.__str__() + '\n'
		tmp += '\n'
		# other subtree alignments
		tmp += str(len(self.otherSuba)) + ' other subtree alignments:\n'
		for sbtrA in self.otherSuba:
			tmp += sbtrA.__str__() + '\n'
		tmp += '\n'

		return tmp

	def splitSuba(self, goldSuba):
		#pdb.set_trace()
		gold, other = [], []
		for suba in self.allSuba:
			offsets = suba.srcOffset[0], suba.tgtOffset[0], suba.srcOffset[1], suba.tgtOffset[1]
			if offsets in goldSuba:
				gold.append(suba)
			else:
				other.append(suba)

		return gold, other


if __name__ == "__main__":
	import sys
	beadList = Bead2.loadData(sys.argv[1])

	for i, bead in enumerate(beadList):
		print "="*30, i, "="*30
		print bead
		#print ' '.join(str(bead.tgtTree).split())
