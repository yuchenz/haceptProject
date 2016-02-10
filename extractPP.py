#!/usr/bin/python2.7

def minimizeSquare(x1, y1, x2, y2, up, left):
	#print x1, y1, x2, y2, ' ==> ',
	newX1, newX2, newY1, newY2 = x1, x2, y1, y2

	for i in xrange(x1, x2 + 1):
		tmp = left[i][y2] if y1 == 0 else left[i][y2] - left[i][y1 - 1]
		if tmp == 0: newX1 += 1
		else: break

	for i in xrange(x2, x1 - 1, -1):
		tmp = left[i][y2] if y1 == 0 else left[i][y2] - left[i][y1 - 1]
		if tmp == 0: newX2 -= 1
		else: break
	
	for j in xrange(y1, y2 + 1):
		tmp = up[x2][j] if x1 == 0 else up[x2][j] - up[x1 - 1][j]
		if tmp == 0: newY1 += 1
		else: break

	for j in xrange(y2, y1 - 1, -1):
		tmp = up[x2][j] if x1 == 0 else up[x2][j] - up[x1 - 1][j]
		if tmp == 0: newY2 -= 1
		else: break
	
	#print newX1, newY1, newX2, newY2
	return tuple((newX1, newY1, newX2 + 1, newY2 + 1))

def extractMinPhrasePairs(wordAlignment, maxWordCnt = 5):
	squareList = set([])
	up = [[0 for col in row] for row in wordAlignment]
	left = [[0 for col in row] for row in wordAlignment]
	corner = [[0 for col in row] for row in wordAlignment]

	for i in xrange(len(wordAlignment)):
		for j in xrange(len(wordAlignment[0])):
			if i == 0:
				up[i][j] = wordAlignment[i][j]
			else:
				up[i][j] = up[i - 1][j] + wordAlignment[i][j]

			if j == 0:
				left[i][j] = wordAlignment[i][j]
			else:
				left[i][j] = left[i][j - 1] + wordAlignment[i][j]

			if i == 0 and j == 0:
				corner[i][j] = wordAlignment[i][j]
			elif i == 0:
				corner[i][j] = left[i][j]
			elif j == 0:
				corner[i][j] = up[i][j]
			else: 
				corner[i][j] = corner[i - 1][j - 1] + up[i - 1][j] + left[i][j - 1] + wordAlignment[i][j]
	
	for i in xrange(len(wordAlignment)):
		for j in xrange(len(wordAlignment[0])):
			for ik in xrange(maxWordCnt + 1):
				if i + ik >= len(corner):
					break
				for jk in xrange(maxWordCnt + 1):
					if j + jk >= len(corner[0]):
						break
					if i == 0 and j == 0:
						partIn = corner[i + ik][j + jk]
						part1, part2 = 0, 0
						part3 = corner[i + ik][-1] - corner[i + ik][j + jk]
						part4 = corner[-1][j + jk] - corner[i + ik][j + jk]
					elif i == 0:
						partIn = corner[i + ik][j + jk] - corner[i + ik][j - 1]
						part1 = 0
						part2 = corner[i + ik][j - 1]
						part3 = corner[i + ik][-1] - corner[i + ik][j + jk]
						part4 = corner[-1][j + jk] - corner[i + ik][j + jk] - corner[-1][j - 1] + corner[i + ik][j - 1]
					elif j == 0:
						partIn = corner[i + ik][j + jk] - corner[i - 1][j + jk]
						part1 = corner[i - 1][j + jk]
						part2 = 0
						part3 = corner[i + ik][-1] - corner[i + ik][j + jk] - corner[i - 1][-1] + corner[i - 1][j + jk]
						part4 = corner[-1][j + jk] - corner[i + ik][j + jk]
					else:
						partIn = corner[i + ik][j + jk] - corner[i + ik][j - 1] - corner[i - 1][j + jk] + corner[i - 1][j - 1]
						part1 = corner[i - 1][j + jk] - corner[i - 1][j - 1]
						part2 = corner[i + ik][j - 1] - corner[i - 1][j - 1]
						part3 = corner[i + ik][-1] - corner[i + ik][j + jk] - corner[i - 1][-1] + corner[i - 1][j + jk]
						part4 = corner[-1][j + jk] - corner[i + ik][j + jk] - corner[-1][j - 1] + corner[i + ik][j - 1]

					if part1 == 0 and part2 == 0 and part3 == 0 and part4 == 0 and partIn > 0:
						squareList.add(minimizeSquare(i, j, i + ik, j + jk, up, left))
	
	return list(squareList)

if __name__ == "__main__":
	A = [[1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0]]
	print extractMinPhrasePairs(A)

