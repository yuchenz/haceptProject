#!/usr/bin/python2.7

import nltk
from Rule import Rule
import util
import sys
import pdb

debug_log = sys.stderr

class Bead:
	def __init__(self, srcTree, tgtTree, wordAlignment, subtreeAlignment, wordRulesFlag, extensiveRulesFlag,  verbose):
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

		:type wordRulesFlag: bool
		:param wordRulesFlag: True means to add word alignments that are not in the subtree alignments into the ruleList,
							False means no;

		class parameters:
		:type self.subtreeAlignmentDic: a dictionary, mapping from a 4-tuple to a list of 4-tuples 
		:param self.subtreeAlignmentDic: each tuple (x1, y1, x2, y2) represents that in the word alignment matrix, from (x1, y1) to (x2, y2) is a subtree; 
									the key tuple is one level upper then its list of tuples

		"""
		self.verbose = verbose

		self.srcTree = srcTree
		self.srcSnt = [word.lower() for word in srcTree.leaves()]
		self.tgtTree = tgtTree
		self.tgtSnt = [word.lower() for word in tgtTree.leaves()]
		self.wordAlignment = wordAlignment
		self.subtreeAlignment = subtreeAlignment
		# adding unary subtree alignments to the list
		#self.subtreeAlignment.extend(util.waMatrix2unarySubtreeAlignments(self.wordAlignment, self.srcTree, self.tgtTree))
		#self.subtreeAlignment = list(set(self.subtreeAlignment))
		
		#pdb.set_trace()
		self.subtreeAlignmentDic = self._level_(self.subtreeAlignment)
		self.ruleList = self._extractRules_(wordRulesFlag, extensiveRulesFlag)

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
		tmp = ''
		'''
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
		'''
		# subtree alignments
		tmp += str(len(self.subtreeAlignment)) + ' subtree alignments:\n'
		for sbtrA in self.subtreeAlignment:
			tmp += str(sbtrA)+'\n'
		tmp += '\n'
		# leveled subtree alignments
		tmp += str(len(self.subtreeAlignmentDic.keys())) + ' leveled subtree alignments:\n'
		for key in self.subtreeAlignmentDic:
			tmp += str(key)+': '+str(self.subtreeAlignmentDic[key])+'\n'
		tmp += '\n'
		# rules
		tmp += str(len(self.ruleList)) + ' rules in the Bead:\n'
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

		:type subtreeAlignment: a list of lists, which contain 4-tuples
		:param subtreeAlignment: each element list is a frame,
								 each tuple (x1, y1, x2, y2) represents the subtree square on the word alignment matrix.

		"""
		for lis in subtreeAlignment:
			lis.sort(key = (lambda x: (x[3] - x[1]) * (x[2] - x[0])), reverse = True)
		subtreeAlignment.sort(key = (lambda x: (x[0][3] - x[0][1]) * (x[0][2] - x[0][0])), reverse = True)

		leveledSubtreeAlignment = {}
		i = 1
		while i < len(subtreeAlignment):
			smallFrame = subtreeAlignment[i]
			for j in xrange(i-1, -1, -1):
				bigFrame = subtreeAlignment[j]
				if cls._inside_(smallFrame[0], bigFrame[0]):
					for bigSquare in bigFrame:
						leveledSubtreeAlignment[bigSquare] = leveledSubtreeAlignment.get(bigSquare, [])
						leveledSubtreeAlignment[bigSquare].append(smallFrame)
					break
			i += 1

		#for key in leveledSubtreeAlignment:
			#leveledSubtreeAlignment[key].sort()
			#print key, ':',
			#print leveledSubtreeAlignment[key]

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

	def _extract_(self, key, subaList):
		subaList.sort()
		lhs = 'X'
		rhsSrc, rhsTgt, align = [], [], []

		#pdb.set_trace()
		i = key[0]
		for square in subaList: 
			if square[0] != i:
				for j in xrange(i, square[0]):
					rhsSrc.append(j)
					if not self.legalRule(rhsSrc + ['placeHolder'], ['placeHolder']): return False   # prune out illegal rules early
			rhsSrc.append('X')
			if not self.legalRule(rhsSrc + ['placeHolder'], ['placeHolder']): return False
			i = square[2]
		if key[2] != i:
			for j in xrange(i, key[2]):
				rhsSrc.append(j)
				if not self.legalRule(rhsSrc + ['placeHolder'], ['placeHolder']): return False

		i = key[1]
		for k, square in enumerate(sorted(subaList, key=lambda x: x[1])):
			if square[1] != i:
				for j in xrange(i, square[1]):
					rhsTgt.append(j)
					if not self.legalRule(['placeHolder'], rhsTgt + ['placeHolder']): return False
			rhsTgt.append('X')
			if not self.legalRule(['placeHolder'], rhsTgt + ['placeHolder']): return False
			align.append((subaList.index(square), k))
			i = square[3]
		if key[3] != i:
			for j in xrange(i, key[3]):
				rhsTgt.append(j)
				if not self.legalRule(['placeHolder'], rhsTgt + ['placeHolder']): return False

		tmpRule = Rule(lhs, rhsSrc, rhsTgt, align, self.wordAlignment, self.srcSnt, self.tgtSnt)
		if self.verbose: print >> debug_log, tmpRule, '\t\t',
		if self.legalRule(rhsSrc, rhsTgt):
			return tmpRule   
		else:
			return False

	def _extractRules_(self, wordRulesFlag, extensiveRulesFlag):
		"""
		Return a list of rules extracted from this bead.

		:type wordRulesFlag: bool
		:param wordRulesFlag: True means to add word alignments that are not in the subtree alignments into the ruleList,
							False means no;

		"""
		ruleList = []
		# add in rules with non-terminal Xs
		for key in self.subtreeAlignmentDic:
			for subaList in util.allCombinations(self.subtreeAlignmentDic[key]):
				if self.verbose: print >> debug_log, key, ':', subaList
				tmpRule = self._extract_(key, subaList)
				if tmpRule: ruleList.append(tmpRule)

		# add in rules with no non-terminal Xs, i.e. rules that are phrase pairs (only phrase pairs that satisfy the tree structures)
		#pdb.set_trace()
		for square in [suba for lis in self.subtreeAlignment for suba in lis]:
			lhs = 'X'
			rhsSrc = range(square[0], square[2])
			rhsTgt = range(square[1], square[3])
			align = []
			tmpRule = Rule(lhs, rhsSrc, rhsTgt, align, self.wordAlignment, self.srcSnt, self.tgtSnt)
			if self.verbose: print >> debug_log, tmpRule, '\t\t',
			if self.legalRule(rhsSrc, rhsTgt):
				ruleList.append(tmpRule)

		# if not wordRulesFlag, only add in rules that are word alignments (i.e. word pairs) but not corresponding subtree alignments
		if self.verbose:
			print >> debug_log, "Bead got wordRulesFlag:", str(wordRulesFlag)
		if not wordRulesFlag:
			if self.verbose: print >> debug_log, "wordRules are:"
			lhs = 'X'
			rhsSrc, rhsTgt, align = [], [], []   # here align is for the alignment of Xs, not word alignment, so keep empty 
			for i in xrange(len(self.wordAlignment)):
				for j in xrange(len(self.wordAlignment[0])):
					if self.wordAlignment[i][j]:
						if sum(self.wordAlignment[i]) == 1 and sum([row[j] for row in self.wordAlignment]) == 1:
							rhsSrc, rhsTgt = [i], [j]
							if self.verbose: print >> debug_log, i, j, self.srcSnt[i], self.tgtSnt[j]
							if self.legalRule(rhsSrc, rhsTgt):
								if self.verbose: print >> debug_log, "legal"
								tmpRule = Rule(lhs, rhsSrc, rhsTgt, align, self.wordAlignment, self.srcSnt, self.tgtSnt)
								ruleList.append(tmpRule)
						break

		# if extensiveRulesFlag, add in extensive rules which include:
		#	- a rule with the determiner ("a" or "the") removed, e.g. given an existing rule "... ||| a peace agreement [X] ||| ...", 
		#			another rule "... ||| peace agreement [X] ||| ..." is added, iff. "a" is not aligned to any foreign words,
		#			word/X alignments and occurences are kept the same;
		if extensiveRulesFlag:
			tmpRuleList = []
			for rule in ruleList:
				if len(rule.rhsTgt) > 1 and rule.rhsTgt[0] in ["a", "the"] \
						and 0 not in [align[1] for align in rule.alignment]:
					tmpRule = Rule(None, None, None, None, None, None, None)
					tmpRule.lhs, tmpRule.rhsSrc, tmpRule.rhsTgt = rule.lhs, rule.rhsSrc, rule.rhsTgt[1:]
					tmpRule.alignment = [(align[0], align[1] - 1) for align in rule.alignment]
					#print tmpRule.alignment
					tmpRuleList.append(tmpRule)
			ruleList.extend(tmpRuleList)

		return ruleList

	def legalRule(self, rhsSrc, rhsTgt):
		'''
		If both rhsSrc and rhsTgt:
			- contain at least 1 but at most 5 terminals, and
			- contain at most 2 non-terminals
			- don't contain two Xs next to each other on the foreign language side
			- don't contain any words longer than 10 characters
		return True
		otherwise, return False
		'''
		numXSrc = rhsSrc.count('X')
		numXTgt = rhsTgt.count('X')
		if numXSrc > 2 or numXTgt > 2:
			if self.verbose: print >> debug_log, "illegal: more than 2 Xs"
			return False
		if len(rhsSrc) - numXSrc > 5 or len(rhsTgt) - numXTgt > 5:
					if self.verbose: print >> debug_log, "illegal: more than 5 terminals"
					return False
		if len(rhsSrc) - numXSrc < 1 or len(rhsTgt) - numXTgt < 1:
					if self.verbose: print >> debug_log, "illegal: less than 1 terminal"
					return False
		if numXSrc == 2 and abs(rhsSrc.index('X') - (len(rhsSrc) - rhsSrc[::-1].index('X') - 1)) == 1:
			if self.verbose: print >> debug_log, "illegal: two Xs next to each other on rhsSrc"
			return False

		for i in rhsSrc:
			if i != 'X' and i != 'placeHolder' and len(self.srcSnt[i]) > 40:
				if self.verbose: print >> debug_log, "illegal: src word longer than 40 characters"
				return False
			elif i != 'X' and i != 'placeHolder' and '|' in self.srcSnt[i]:
				if self.verbose: print >> debug_log, "illegal: src side contains '|'"
				return False

		for i in rhsTgt:
			if i != 'X' and i != 'placeHolder' and len(self.tgtSnt[i]) > 40:
				if self.verbose: print >> debug_log, "illegal: tgt word longer than 40 characters"
				return False
			elif i != 'X' and i != 'placeHolder' and '|' in self.tgtSnt[i]:
				if self.verbose: print >> debug_log, "illegal: tgt side contains '|'"
				return False

		if self.verbose: print >> debug_log, "legal"

		return True


if __name__ == "__main__":
	import sys
	beadList = Bead.loadData(sys.argv[1])

	for i, bead in enumerate(beadList):
		print "="*30, i, "="*30
		print bead
		#print ' '.join(str(bead.tgtTree).split())
