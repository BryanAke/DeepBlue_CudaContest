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


#deterine how ordered the list is 

