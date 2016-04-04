
def parseNode(node, ID):
	res = []
	node = [part.split('-') for part in node.split('+')]
	for i, part in enumerate(node):
		featID = 'f' + str(ID)

		for j, subp in enumerate(part):
			if j == 1: featID += '-'
			res.append(featID + '=' + subp)
	
	return res

def feat_srcHead(bead, suba, ID):
	featList = parseNode(bead.srcTree[suba.srcTreePosition].node, ID)
	return featList 

def feat_tgtHead(bead, suba, ID):
	featList = parseNode(bead.tgtTree[suba.tgtTreePosition].node, ID)
	return featList

def feat_sameHead(srcHeads, tgtHeads, ID):
	tmp1, tmp1_, tmp2, tmp2_ = [], [], [], []
	res = []

	for sH in srcHeads:
		sH = sH.split('=')
		if '-' in sH[0]: tmp1_.append(sH[1])
		else: tmp1.append(sH[1])
	
	for tH in tgtHeads:
		tH = tH.split('=')
		if '-' in tH[0]: tmp2_.append(tH[1])
		else: tmp2.append(tH[1])
	
	for sH in tmp1:
		if sH in tmp2:
			res.append('f' + str(ID) + '=True')
			break
	else:
		res.append('f' + str(ID) + '=False')
	
	for sH in tmp1_:
		if sH in tmp2_:
			res.append('f' + str(ID + 1) + '=True')
			break
	else:
		if tmp1_ == [] or tmp2_ == []:
			res.append('f' + str(ID + 1) + '=None')
		else:
			res.append('f' + str(ID + 1) + '=False')
	
	return res

def unalignedWords(bead, suba):
	srcUnaligned, tgtUnaligned = [], []
	srcStart, srcEnd, tgtStart, tgtEnd = -1, -1, -1, -1

	for i in xrange(suba.srcOffset[0], suba.srcOffset[1]):
		if sum(bead.wordAlignment[i][suba.tgtOffset[0]:suba.tgtOffset[1]]) == 0:
			srcUnaligned.append(i)
		else:
			if srcStart == -1: srcStart = i
			srcEnd = i
	
	for j in xrange(suba.tgtOffset[0], suba.tgtOffset[1]):
		#print len(bead.wordAlignment), len(bead.wordAlignment[0]), suba.srcOffset, suba.tgtOffset, j
		if sum([bead.wordAlignment[k][j] for k in xrange(suba.srcOffset[0], suba.srcOffset[1])]) == 0:
			tgtUnaligned.append(j)
		else:
			if tgtStart == -1: tgtStart = j
			tgtEnd = j
	
	return srcUnaligned, tgtUnaligned, srcStart, srcEnd, tgtStart, tgtEnd

def feat_frontUnalignedWord(unaligned, start, snt, ID):
	result = []
	for i in unaligned:
		if i < start:
			result.append('f' + str(ID) + '=' + snt[i])
	return result

def feat_backUnalignedWord(unaligned, end, snt, ID):
	result = []
	for i in unaligned:
		if i > end:
			result.append('f' + str(ID) + '=' + snt[i])
	return result

def feat_midUnalignedWord(unaligned, start, end, snt, ID):
	result = []
	for i in unaligned:
		if i > start and i < end:
			result.append('f' + str(ID) + '=' + snt[i])
	return result

def feat_alignedPosPair(bead, suba, ID):
	result = []
	srcPos = [bead.srcTree[leaf[:-1]].node for leaf in bead.srcTree.treepositions('leaves')]
	tgtPos = [bead.tgtTree[leaf[:-1]].node for leaf in bead.tgtTree.treepositions('leaves')]

	for i in xrange(suba.srcOffset[0], suba.srcOffset[1]):
		for j in xrange(suba.tgtOffset[0], suba.tgtOffset[1]):
			if bead.wordAlignment[i][j]:
				result.append('f' + str(ID) + '=' + srcPos[i] + '_' + tgtPos[j])
	
	return result
				
def feat_largeCoverSpan(bead, suba, ID):
	srcLen, tgtLen = len(bead.srcSnt), len(bead.tgtSnt)
	if suba.srcOffset[1] - suba.srcOffset[0] > srcLen * 0.5 and suba.tgtOffset[1] - suba.tgtOffset[0] > tgtLen * 0.5:
		return 'f' + str(ID) + '=True'
	else:
		return 'f' + str(ID) + '=False'

def feat_wholeSentCoverSpan(bead, suba, ID):
	srcLen, tgtLen = len(bead.srcSnt), len(bead.tgtSnt)
	if suba.srcOffset == (0, srcLen) and suba.tgtOffset == (0, tgtLen):
		return 'f' + str(ID) + '=True'
	else:
		return 'f' + str(ID) + '=False'

def feat_smallestBlockCoverCnt(bead, suba, ID):
	smallestBlockCnt = {}
	for sub in bead.allSuba:
		smallestBlockCnt[sub.smallestBlock] = smallestBlockCnt.get(sub.smallestBlock, 0) + 1
	return 'f' + str(ID) + '=' + str(smallestBlockCnt[suba.smallestBlock])

def feat_alwaysON(ID):
	return 'f' + str(ID) + '=True'

def features(bead, suba):
	featList = []
	ID = 0

	srcHeads = feat_srcHead(bead, suba, ID)
	featList.extend(srcHeads); ID += 1
	tgtHeads = feat_tgtHead(bead, suba, ID)
	featList.extend(tgtHeads); ID += 1

	featList.extend(feat_sameHead(srcHeads, tgtHeads, ID)); ID += 2

	srcUnaligned, tgtUnaligned, srcStart, srcEnd, tgtStart, tgtEnd = unalignedWords(bead, suba)

	featList.extend(feat_frontUnalignedWord(tgtUnaligned, tgtStart, bead.tgtSnt, ID)); ID += 1
	featList.extend(feat_frontUnalignedWord(srcUnaligned, srcStart, bead.srcSnt, ID)); ID += 1
	featList.extend(feat_backUnalignedWord(tgtUnaligned, tgtEnd, bead.tgtSnt, ID)); ID += 1
	featList.extend(feat_backUnalignedWord(srcUnaligned, srcEnd, bead.srcSnt, ID)); ID += 1
	featList.extend(feat_midUnalignedWord(tgtUnaligned, tgtStart, tgtEnd, bead.tgtSnt, ID)); ID += 1
	featList.extend(feat_midUnalignedWord(srcUnaligned, srcStart, srcEnd, bead.srcSnt, ID)); ID += 1

	featList.extend(feat_alignedPosPair(bead, suba, ID)); ID += 1

	featList.append(feat_largeCoverSpan(bead, suba, ID)); ID += 1
	featList.append(feat_wholeSentCoverSpan(bead, suba, ID)); ID += 1

	featList.append(feat_smallestBlockCoverCnt(bead, suba, ID)); ID += 1

	featList.append(feat_alwaysON(ID))

	return featList
