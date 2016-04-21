#!/usr/bin/python2.7

def mergeIt(diffWaF, interWaF, outF):
	diffL = [line.split() for line in open(diffWaF).readlines()]
	interL = [line.split() for line in open(interWaF).readlines()]

	f = open(outF, 'w')
	for i in xrange(len(diffL)):
		f.write(' '.join(list(set(diffL[i]).union(set(interL[i])))) + '\n')
	
	for j in xrange(i + 1, len(interL)):
		f.write(' '.join(interL[j]) + '\n')

	f.close()

if __name__ == "__main__":
	import sys
	mergeIt(sys.argv[1], sys.argv[2], sys.argv[3])
