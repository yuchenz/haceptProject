#!/usr/bin/python2.7

def diffIt(gdfaWaF, interWaF, outF):
	gdfaL = [line.split() for line in open(gdfaWaF).readlines()]
	interL = [line.split() for line in open(interWaF).readlines()]

	f = open(outF, 'w')
	for i in xrange(len(interL)):
		f.write(' '.join(list(set(gdfaL[i]).difference(set(interL[i])))) + '\n')
	f.close()

if __name__ == "__main__":
	import sys
	diffIt(sys.argv[1], sys.argv[2], sys.argv[3])
