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

		
