import knowledge_base

threshold = 10
def adjacent_inversions(rack):
	order = 0;
	for i in xrange(len(rack)-1):
		if rack[i] > rack[i+1]:
			order+=1
	return order

def closest_indecies(rack):
	#returns the indecies of the rack that have numbers
	#that are closest together
	dist = 100
	for i in xrange(len(rack)-1):
		if rack[i+1]:#check if we're in range
			if (rack[i+1]-rack[i]) < dist:
				ret = (i,i+1)
				dist = rack[i+1]-rack[i]
	return ret


#deterine whether to use the 'normal' distibution to model
#(which uses the happiness function) or whether to use the
#'relative' distribution model (which fits places cards based
#on their best relative location
def normal_or_relative(rack):
	#0: use normal distibution
	#1: use relative distribution
	if adjacent_inversions(rack) < threshold:
		#then the rack is pretty sorted
		return 1
	return 0

#check to see where the best location for a card would be
#in the deck
def best_fit(card, rack):
	if (not normal_relative(rack)):
		#use the happiness function
		#return the position
		print "Holding place"
	#use the relative function
	runs = getRunsAdjacentToRuns(rack)
	if runs:
		for tup in runs:
			if card in tup:
				return rack.index(card)
			elif True in knowledge.impossibilities and rack.index(True):
				print "Holder 2"


def closestValidFit(card,rack):
	#return index of location that best fits
	for i in xrange(len(rack)-1):
		if card > rack[i]:
			continue
		if i==0:
			return i
		return (i-1)
	return 0

def getScore(rack):
	score = 0
	for i in xrange(len(rack)-1):
		if rack[i+1]:
			if rack[i]<rack[i+1]:
				score = score+1
	return score

def getOrderedScore(rack,card):
	score = 0
	ndx = closestValidFit(card, rack)
	tmp = rack[ndx]
	rack[ndx] = card
	res = getScore(rack)
	rack[ndx] = tmp
	return res

#define a function that returns the probability of a run (2 or more cards ever extending to a run of 5
#if the probability is zero then exclude it

def getHappiness(card, index):
	return 1.0 - abs(((card/knowledge_base.kCardCount) - ((index+1)/knowledge_base.kRackSize)))

