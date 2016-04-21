#!/usr/bin/python2.7

def eval(goldF, autoF):
	goldWA = [set(line.split()) for line in open(goldF).readlines()]
	autoWA = [set(line.split()) for line in open(autoF).readlines()]

	assert len(goldWA) == len(autoWA), "len goldWA == %d, len autoWA == %d" % (len(goldWA), len(autoWA))

	truePositive = 0
	falsePositive = 0
	falseNegative = 0
	for gwa, awa in zip(goldWA, autoWA):
		truePositive += len(list(gwa.intersection(awa)))
		falsePositive += len(list(awa.difference(gwa)))
		falseNegative += len(list(gwa.difference(awa)))
	
	p = truePositive * 1.0 / (truePositive + falsePositive)
	r = truePositive * 1.0 / (truePositive + falseNegative)
	print "truePositive, falsePositive, falseNegative == ", truePositive, falsePositive, falseNegative  
	print "p, r, f == %.2f, %.2f, %.2f" % (p, r, 2 * p * r / (p + r))

if __name__ == '__main__':
	import sys
	goldF = sys.argv[1]
	autoF = sys.argv[2]
	eval(goldF, autoF)
