import sys

def extractLabels(tgtTree):
	targetTopLabelCollection = set([])
	targetLabelCollection = set([])

	# collect all top labels and regular labels on the target language
	#if verbose: print >> sys.stderr, ' '.join(sntFrame.tgtTree.pprint().split())
	children = [tgtTree] 
	while len(children) == 1:
		label = children[0].node
		if len(label) == 0: label = 'Top'
		targetTopLabelCollection.add(label)
		targetLabelCollection.add(label)
		tgtTree = children[0]
		if tgtTree.height() <= 2: break
		children = [child for child in tgtTree]

	for subtr in tgtTree.subtrees():
		label = subtr.node
		if len(label) == 0: label = 'TOP'
		targetLabelCollection.add(label)
	
	return targetTopLabelCollection, targetLabelCollection

def generateBasicGlueRules(targetTopLabelCollection, targetLabelCollection, verbose):
	if verbose: 
		print >> sys.stderr, "\ngenerating basic glue rules ...\n"
		print >> sys.stderr, "targetTopLabelCollection:"
		print >> sys.stderr, targetTopLabelCollection
		print >> sys.stderr, "targetLabelCollection:"
		print >> sys.stderr, targetLabelCollection
		print >> sys.stderr

	ruleList = []

	# choose a top label that is not already a label
	topLabel = "QQQQQQ"
	for i in xrange(1, len(topLabel)):
		if topLabel[:i] not in targetLabelCollection:
			topLabel = topLabel[:i]
			break

	# basic rules:
	ruleList.append("<s> [X] ||| <s> [" + topLabel + "] ||| 1 ||| 0-0\n")
	ruleList.append("[X][" + topLabel + "] </s> [X] ||| [X][" + topLabel + "] </s> [" + topLabel + "] ||| 1 ||| 0-0\n")

	# top rules:
	for label in targetTopLabelCollection:
		ruleList.append("<s> [X][" + label + "] </s> [X] ||| <s> [X][" + label + "] </s> [" + topLabel + "] ||| 1 ||| 0-0 1-1 2-2\n")

	# glue rules:
	for label in targetLabelCollection:
		ruleList.append("[X][" + topLabel + "] [X][" + label + "] [X] ||| [X][" + topLabel + "] [X][" + label + "] [" + topLabel + "] ||| 2.718 ||| 0-0 1-1\n")
	# glue rule for unknown words
	ruleList.append("[X][" + topLabel + "] [X][X] [X] ||| [X][" + topLabel + "] [X][X] [" + topLabel + "] ||| 2.718 ||| 0-0 1-1\n")

	return ruleList


