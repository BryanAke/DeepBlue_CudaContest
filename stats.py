import collections
import pickle
import sys

with open(sys.argv[1]) as f:
	k = pickle.load(f)

# Draws v. Takes
draw = collections.Counter()
for m in k.moves:
	if m[0]:
		draw[m[1]] += 1

print draw
