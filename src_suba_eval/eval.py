#!/usr/bin/python2.7

import pdb

def eval(gsubaFile, autoFile):
	gsubaList = [line.split() for line in open(gsubaFile).readlines()]
	#pdb.set_trace()
	tmp = [line.split() for line in open(autoFile).readlines()]
	tmp = [line[0].split('--') + line[1:] for line in tmp]
	tmp = [(line[0][2:], line[1]) for line in tmp if float(line[-1]) <= float(line[-3])]
	if tmp == []:
		print "no True testing examples!!!"
		exit(0)

	autoSubaList = []
	sentID = -1
	for line in tmp:
		if line[0] != str(sentID):
			sentID += 1
			autoSubaList.append([])
		autoSubaList[-1].append(line[1])

	assert len(autoSubaList) == len(gsubaList), "len autoSubaList == %d, len gsubaList == %d" % (len(autoSubaList), len(gsubaList))

	goldTrue = 0
	autoTrue = 0
	correctTrue = 0
	pairList = zip(gsubaList, autoSubaList)
	for pair in pairList:
		goldTrue += len(pair[0])
		autoTrue += len(pair[1])
		correctTrue += len(list(set(pair[0]).intersection(set(pair[1]))))
	
	print "goldTrue == %d\nautoTrue == %d\ncorrectTrue == %d\n\n" % (goldTrue, autoTrue, correctTrue)
	p = correctTrue * 1.0 / autoTrue
	r = correctTrue * 1.0 / goldTrue
	f = 2 * p * r / (p + r)
	print "p == %.2f\nr == %.2f\nf == %.2f\n" % (p, r, f)

if __name__ == "__main__":
	import sys
	eval(sys.argv[1], sys.argv[2])
