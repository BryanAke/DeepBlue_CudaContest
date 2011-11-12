def adjacent_inversions(rack):
	order = 0;
	for i in xrange(len(rack)-1):
		if rack[i] > rack[i+1]:
			order+=1
	return order

def closest_indecies(rack):
	#returns the indecies of the rack that have numbers 
			
