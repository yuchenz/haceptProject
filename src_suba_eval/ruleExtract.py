#!/usr/bin/python2.7

import re
from Rule import Rule
from util import oneline2waMatrix

def _inside_(currentSquare, square):
	"""
	Return if currentSquare is inside square.

	:type currentSquare: 4-tuple
	:param currentSquare: (x1, x2, y1, y2) representing a subtree square on the word alignment matrix

	:type square: 4-tuple
	:param square: (x1, x2, y1, y2) representing a subtree square on the word alignment matrix

	"""
	if currentSquare[0] >= square[0] and \
			currentSquare[1] <= square[1] and \
			currentSquare[2] >= square[2] and \
			currentSquare[3] <= square[3]:
				return True
	else:
		return False

def _level_(subtreeAlignment):
	"""
	Return a sorted and leveled subtree alignment dictionary.

	:type subtreeAlignment: a list of lists 
	:param subtreeAlignment: each element list is a subtree pair [x1, x2, y1, y2], representing the subtree square on the word alignment matrix.

	"""
	subtreeAlignment.sort(key = (lambda x: (x[3] - x[2]) * (x[1] - x[0])), reverse = True)

	leveledSubtreeAlignment = {}
	i = 1
	while i < len(subtreeAlignment):
		smallSquare = tuple(subtreeAlignment[i])
		for j in xrange(i-1, -1, -1):
			bigSquare = tuple(subtreeAlignment[j])
			if _inside_(smallSquare, bigSquare):
				leveledSubtreeAlignment[bigSquare] = leveledSubtreeAlignment.get(bigSquare, [])
				leveledSubtreeAlignment[bigSquare].append(smallSquare)
				break
		i += 1

	return leveledSubtreeAlignment

def _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, status):
	'''
	if both rhsSrc and rhsTgt:
		- contain at most 5 terminals, and
		- (status == partial) or (status == complete && contain at least 1 terminal), and
		- contain at most 2 non-terminals
		- don't contain two Xs next to each other on rhsSrc
		- don't contain words that are longer than 40 characters
	return True
	otherwise, return False
	'''
	numXSrc = rhsSrc.count('X') 
	numXTgt = rhsTgt.count('X')

	if numXSrc > 2 or numXTgt > 2: return False
	if len(rhsSrc) - numXSrc > 5 or len(rhsTgt) - numXTgt > 5: return False
	if status == 'complete' and (len(rhsSrc) - numXSrc < 1 or len(rhsTgt) - numXTgt < 1): return False
	if 'XX' in ''.join([str(item) for item in rhsSrc]): return False

	tmp = [len(chSent[i]) for i in rhsSrc if not isinstance(i, str)]; tmp.append(1)
	if max(tmp) > 40: return False
	tmp = [len(enSent[i]) for i in rhsTgt if not isinstance(i, str)]; tmp.append(1)
	if max(tmp) > 40: return False

	return True

def _extract_(bigSquare, smallSquareList, chSent, enSent, wordAlignment):
	lhsSrc, lhsTgt = 'X', 'X'
	rhsSrc, rhsTgt, align = [], [], []

	i = bigSquare[0]
	for square in smallSquareList:
		if square[0] != i:
			for j in xrange(i, square[0]):
				rhsSrc.append(j)
				if not _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'partial'):   # this is a partially built rule, not finished yet
					return None

		rhsSrc.append('X')
		if not _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'partial'):   # this is a partially built rule, not finished yet
			return None

		i = square[1]
	
	if bigSquare[1] != i:
		for j in xrange(i, bigSquare[1]):
			rhsSrc.append(j)
			if not _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'partial'):   # this is a partially built rule, not finished yet
				return None
	
	i = bigSquare[2]
	for k, square in enumerate(sorted(smallSquareList, key = lambda x: x[2])):
		if square[2] != i:
			for j in xrange(i, square[2]):
				rhsTgt.append(j)
				if not _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'partial'):   # this is a partially built rule, not finished yet
					return None

		rhsTgt.append('X')
		if not _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'partial'):   # this is a partially built rule, not finished yet
			return None

		align.append((smallSquareList.index(square), k))
		i = square[3]

	if bigSquare[3] != i:
		for j in xrange(i, bigSquare[3]):
			rhsTgt.append(j)
			if not _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'partial'):   # this is a partially built rule, not finished yet
				return None

	if _isLegalRule_(rhsSrc, rhsTgt, chSent, enSent, 'complete'):
		return Rule(lhsSrc, lhsTgt, rhsSrc, rhsTgt, align, wordAlignment, chSent, enSent, bigSquare)

def extractRules(chF, enF, subaF, waF):
	chSentList = [line.split() for line in codecs.open(chF, 'r', 'utf-8').readlines()]
	enSentList = [line.split() for line in codecs.open(enF, 'r', 'utf-8').readlines()]
	subaList = [[item.split('-') for item in line.split()] for line in codecs.open(subaF, 'r', 'utf-8').readlines()]
	subaList = [[[int(d) for d in item] for item in line] for line in subaList]
	waList = [line for line in codecs.open(waF, 'r', 'utf-8').readlines()]

	assert len(chSentList) == len(enSentList) == len(subaList) == len(waList), \
			"len(chSentList) == %d, len(enSentList) == %d, len(subaList) == %d, len(waList) == %d" % (len(chSentList), len(enSentList), len(subaList), len(waList))

	ruleList = []

	for i in xrange(len(subaList)):
		#print i,
		# rules with non-terminal Xs
		subaDic = _level_(subaList[i])
		waMatrix = oneline2waMatrix(waList[i], len(chSentList[i]), len(enSentList[i]))
		for bigSquare in subaDic:
			rule = _extract_(bigSquare, subaDic[bigSquare], chSentList[i], enSentList[i], waMatrix) 
			if rule: ruleList.append(rule)
	
		# rules without non-terminal Xs
		for square in subaList[i]:
			lhsSrc, lhsTgt = 'X', 'X'
			rhsSrc = range(square[0], square[1])
			rhsTgt = range(square[2], square[3])
			align = []
			if _isLegalRule_(rhsSrc, rhsTgt, chSentList[i], enSentList[i], "complete"):
				rule = Rule(lhsSrc, lhsTgt, rhsSrc, rhsTgt, align, waMatrix, chSentList[i], enSentList[i], square) 
				ruleList.append(rule)

	return ruleList


if __name__ == "__main__":
	import sys
	import codecs

	chF = sys.argv[1]
	enF = sys.argv[2]
	subaF = sys.argv[3]
	waF = sys.argv[4]
	
	ruleList = extractRules(chF, enF, subaF, waF)

	ans, ans1 = [], []
	for rule in ruleList:
		ruleNInv, ruleInv = rule.mosesFormatRule()
		ans.append(ruleNInv)
		ans1.append(ruleInv)
	
	# change '-lbr-' into '(', '-rbr-' into ')', and '-at-' into '@'
	for i, a in enumerate(ans):
		a = re.sub('-lbr-', '(', a)
		a = re.sub('-rbr-', ')', a)
		ans[i] = re.sub('-at-', '@', a)
	for i, a in enumerate(ans1):
		a = re.sub('-lbr-', '(', a)
		a = re.sub('-rbr-', ')', a)
		ans1[i] = re.sub('-at-', '@', a)

	ans.sort(); ans1.sort()
	for a in ans:
		print >> sys.stdout, a.encode('utf-8'),
	for a in ans1:
		print >> sys.stderr, a.encode('utf-8'),

