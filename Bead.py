#!/usr/bin/python2.7

import nltk
from Rule import Rule
import util

class Bead:
	def __init__(self, srcTree, tgtTree, wordAlignment, subtreeAlignment, wordRulesFlag=False):
		"""
		Initialize a Bead instance.
		
		:type srcTree: nltk.ParentedTree
		:param srcTree: constitutent phrased-based (gold or parsed) tree on the source language (e.g. ch);

		:type srcTree: nltk.ParentedTree
		:param srcTree: constitutent phrased-based (gold or parsed) tree on the target language (e.g. en);

		:type wordAlignment: a list of lists
		:param wordAlignment: alignment between words, i.e. a matrix A,
								where A[i][j] == 1 indicates source word i is aligned with target word j; 

		:type subtreeAlignment: a list of 4-tuples
		:param subtreeAlignment: each tuple (x1, y1, x2, y2) represents the subtree square on the word alignment matrix.

		:type wordRulesFlag: bool
		:param wordRulesFlag: True means to add word alignments that are not in the subtree alignments into the ruleList,
							False means no;

		class parameters:
		:type self.subtreeAlignmentDic: a dictionary, mapping from a 4-tuple to a list of 4-tuples 
		:param self.subtreeAlignmentDic: each tuple (x1, y1, x2, y2) represents that in the word alignment matrix, from (x1, y1) to (x2, y2) is a subtree; 
									the key tuple is one level upper then its list of tuples

		"""
		self.srcTree = srcTree
		self.srcSnt = [word.lower() for word in srcTree.leaves()]
		self.tgtTree = tgtTree
		self.tgtSnt = [word.lower() for word in tgtTree.leaves()]
		self.wordAlignment = wordAlignment
		self.subtreeAlignment = subtreeAlignment
		# adding unary subtree alignments to the list
		self.subtreeAlignment.extend(util.waMatrix2unarySubtreeAlignments(self.wordAlignment, self.srcTree, self.tgtTree))
		self.subtreeAlignment = list(set(self.subtreeAlignment))
		
		self.subtreeAlignmentDic = self._level_(self.subtreeAlignment)
		self.ruleList = self._extractRules_(wordRulesFlag)

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
		blocks = util.cleanData(f.read()).split('\n\n')
		f.close()

		beadList = []

		srcTree = None
		tgtTree = None
		wordAlignment = None 
		subtreeAlignment = [] 

		for block in blocks[:-1]:
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
					
			if not errFlag:
				beadList.append(cls(srcTree, tgtTree, wordAlignment, subtreeAlignment))
			srcTree, tgtTree, wordAlignment, subtreeAlignment = None, None, None, []

		return beadList
	
	def __str__(self):
		# src tree
		tmp = self.srcTree.pprint().encode('utf-8')+"\n\n"
		# tgt tree
		tmp += self.tgtTree.pprint().encode('utf-8')+"\n\n"
		# word alignment matrix
		for i in xrange(len(self.wordAlignment)):
			for j in xrange(len(self.wordAlignment[i])):
				tmp += str(self.wordAlignment[i][j])+' '
			tmp += '\n'
		tmp += '\n'
		# subtree alignments
		for sbtrA in self.subtreeAlignment:
			tmp += str(sbtrA)+'\n'
		tmp += '\n'
		# leveled subtree alignments
		for key in self.subtreeAlignmentDic:
			tmp += str(key)+': '+str(self.subtreeAlignmentDic[key])+'\n'
		tmp += '\n'
		# rules
		for rule in self.ruleList:
			tmp += rule.lhs + ' -> '
			tmp += ' '.join([item.encode('utf-8') for item in rule.rhsSrc]) + ' | ' 
			tmp += ' '.join([item.encode('utf-8') for item in rule.rhsTgt]) + ' | ' 
			tmp += ' '.join([str(item) for item in rule.alignment]) + '\n'
		tmp += '\n'

		return tmp

	@classmethod
	def _level_(cls, subtreeAlignment):
		"""
		Return a sorted and leveled subtree alignment dictionary.

		:type subtreeAlignment: a list of 4-tuples
		:param subtreeAlignment: each tuple (x1, y1, x2, y2) represents the subtree square on the word alignment matrix.

		"""
		subtreeAlignSquareList = sorted(subtreeAlignment, key=(lambda x: (x[3]-x[1])*(x[2]-x[0])), reverse=True)

		leveledSubtreeAlignment = {}
		i = 1
		while i < len(subtreeAlignSquareList):
			square = subtreeAlignSquareList[i]
			for j in xrange(i-1, -1, -1):
				if cls._inside_(square, subtreeAlignSquareList[j]):
					leveledSubtreeAlignment[subtreeAlignSquareList[j]] = leveledSubtreeAlignment.get(subtreeAlignSquareList[j], [])
					leveledSubtreeAlignment[subtreeAlignSquareList[j]].append(square)
					break
			i += 1

		for key in leveledSubtreeAlignment:
			leveledSubtreeAlignment[key].sort()

		return leveledSubtreeAlignment

	@classmethod
	def _inside_(cls, currentSquare, square):
		"""
		Return if currentSquare is inside square.

		:type currentSquare: 4-tuple
		:param currentSquare: (x1, y1, x2, y2) representing a subtree square on the word alignment matrix

		:type square: 4-tuple
		:param square: (x1, y1, x2, y2) representing a subtree square on the word alignment matrix

		"""
		if currentSquare[0] >= square[0] and \
				currentSquare[1] >= square[1] and \
				currentSquare[2] <= square[2] and \
				currentSquare[3] <= square[3]:
					return True
		else:
			return False

	def _extractRules_(self, wordRulesFlag):
		"""
		Return a list of rules extracted from this bead.

		:type wordRulesFlag: bool
		:param wordRulesFlag: True means to add word alignments that are not in the subtree alignments into the ruleList,
							False means no;

		"""
		ruleList = []
		# add in rules with non-terminal Xs
		for key in self.subtreeAlignmentDic:
			lhs = 'X'
			rhsSrc, rhsTgt, align = [], [], []

			i = key[0]
			for square in self.subtreeAlignmentDic[key]:
				if square[0] != i:
					for j in xrange(i, square[0]):
						rhsSrc.append(j)
				rhsSrc.append('X')
				i = square[2]
			if key[2] != i:
				for j in xrange(i, key[2]):
					rhsSrc.append(j)

			i = key[1]
			for k, square in enumerate(sorted(self.subtreeAlignmentDic[key], key=lambda x: x[1])):
				if square[1] != i:
					for j in xrange(i, square[1]):
						rhsTgt.append(j)
				rhsTgt.append('X')
				align.append((self.subtreeAlignmentDic[key].index(square), k))
				i = square[3]
			if key[3] != i:
				for j in xrange(i, key[3]):
					rhsTgt.append(j)

			if self.legalRule(rhsSrc, rhsTgt):
				ruleList.append(Rule(lhs, rhsSrc, rhsTgt, align, self.wordAlignment, self.srcSnt, self.tgtSnt))

		# add in rules with no non-terminal Xs, i.e. rules that are phrase pairs
		for key in self.subtreeAlignmentDic:
			lhs = 'X'
			rhsSrc, rhsTgt, align = [], [], []   # here align is for the alignment of Xs, not word alignment, so keep empty 
			for square in self.subtreeAlignmentDic[key]:
				if square not in self.subtreeAlignmentDic:
					rhsSrc = range(square[0], square[2])
					rhsTgt = range(square[1], square[3])
					if self.legalRule(rhsSrc, rhsTgt):
						ruleList.append(Rule(lhs, rhsSrc, rhsTgt, align, self.wordAlignment, self.srcSnt, self.tgtSnt))

		# if wordRulesFlag, add in rules that are word alignments (i.e. word pairs) but are not subtree alignments
		if wordRulesFlag:
			lhs = 'X'
			rhsSrc, rhsTgt, align = [], [], []   # here align is for the alignment of Xs, not word alignment, so keep empty 
			for i in xrange(len(self.wordAlignment)):
				for j in xrange(len(self.wordAlignment[0])):
					if self.wordAlignment[i][j]:
						if sum(self.wordAlignment[i]) == 1 and sum([row[j] for row in self.wordAlignment]) == 1:
							rhsSrc, rhsTgt = [i], [j]
							tmpRule = Rule(lhs, rhsSrc, rhsTgt, align, self.wordAlignment, self.srcSnt, self.tgtSnt)
							if self.legalRule(rhsSrc, rhsTgt):
								ruleList.append(tmpRule)
						break

		return ruleList

	def legalRule(self, rhsSrc, rhsTgt):
		'''
		If both rhsSrc and rhsTgt:
			- contain at least 1 but at most 5 terminals, and
			- contain at most 2 non-terminals
			- don't contain any words longer than 10 characters
		return True
		otherwise, return False
		'''
		numXSrc = rhsSrc.count('X')
		numXTgt = rhsTgt.count('X')
		if numXSrc > 2 or numXTgt > 2:
			return False
		if len(rhsSrc) - numXSrc > 5 or len(rhsSrc) - numXSrc < 1 or \
				len(rhsTgt) - numXTgt > 5 or len(rhsTgt) - numXTgt < 1:
					return False
		for i in rhsSrc:
			if i != 'X' and len(self.srcSnt[i]) > 10:
				return False
			elif i != 'X' and '|' in self.srcSnt[i]:
				return False

		for i in rhsTgt:
			if i != 'X' and len(self.tgtSnt[i]) > 10:
				return False
			elif i != 'X' and '|' in self.tgtSnt[i]:
				return False

		return True


if __name__ == "__main__":
	import sys
	beadList = Bead.loadData(sys.argv[1])

	for i, bead in enumerate(beadList):
		print "="*30, i, "="*30
		print bead
		#print ' '.join(str(bead.tgtTree).split())
