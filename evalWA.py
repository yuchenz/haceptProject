#!/usr/bin/python2.7

import sys

def evalWA(autoF, goldF):
	truePositive = 0.0
	falsePositive = 0.0
	falseNegative = 0.0
	for auto, gold in zip(open(autoF), open(goldF)):
		auto = set([(pair.split('-')[0], pair.split('-')[1]) for pair in auto.split()])
		gold = set([(pair.split('-')[0], pair.split('-')[1]) for pair in gold.split()])

		truePositive += len(auto.intersection(gold))
		falsePositive += len(auto.difference(gold))
		falseNegative += len(gold.difference(auto))

	p = truePositive / (truePositive + falsePositive)
	r = truePositive / (truePositive + falseNegative)
	print 'p = ', p
	print 'r = ', r
	print 'f = ', 2 * p * r / (p + r)

if __name__ == '__main__':
	evalWA(sys.argv[1], sys.argv[2])
