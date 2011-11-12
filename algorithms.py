import knowledge_base

threshold = 10
def adjacent_inversions(rack, idx=None, card=None):
	order = 0;
	temp = None
	if idx != None:
		temp = rack[idx]
		rack[idx] = card
	
	for i in xrange(len(rack)-1):
		if rack[i] > rack[i+1]:
			order+=1
			
	if idx != None:
		rack[idx]= temp
		
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


def checkDiscard(num):
	for elem in self.discard_pile:
		if num is elem:
			return true
	for elem in self.other_rack:
		if num is elem:
			return true
	return false
	
#find out whether 5 card run is possible to create
def getRunCompletion(run):
	ascend = range(run[-1]+1,run[0]+5)
	decend = range(run[0]-1,run[-1]-5,-1)
	a = false
	d = false
	if (run[0]+5) <= 80:
		for num in ascend:
			if checkDiscard(num):
				continue
			a = true
	if (run[-1]-5) >=1:
		for num in decend:
			if checkDiscard(num):
				continue
			d = true
	res = (a,d)
	return res

def getHappiness(card, index):
	return 1.0 - abs(((card/knowledge_base.kCardCount) - ((index+1)/knowledge_base.kRackSize)))
	
