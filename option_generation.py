# CMDA capstone option generation / scoring function


def increment_index(indices, options, incr_index):
	
	if (indices[incr_index] + 1) < len(options[incr_index]):
		indices[incr_index] += 1
		return indices
	else if (indices[incr_index] + 1) == len(options[incr_index]:
		if (incr_index + 1) == len(indices):
			return None
		indices[incr_index] = 0
		return increment_index(indices, options, incr_index + 1)

# arguments passed in should be a list of tuplets of shortages
# of form (unit, asset type)
def generate_options(empty_spots):
	best_option = null
	best_option_score = 0
	
	
	# an "option" is defined as a list of asset IDs, the unit they
	# are transferring from, and the unit they are transferring to 
	
	# for each loop going through each shortage, finding 
	# all feasible options for each shortage 
	
	# storing options for each spot in a dict keyed by spot order,
	# with an array stored
	spot_options = {}
	spot_id = 0
	for spot in empty_spots:
		# spot is a tuplet of unit, and asset type
		spot_options[spot_id] = [None]
		
		unit_list = list_of_units_query()
		for unit in unit_list:
		
			if unit != spot(unit):
			
				for asset in unit(assets):
				
					if asset.type == spot(asset_type):
						# each alternative stored as a triplet 
						# form (asset, unit from, unit to)
						spot_options[spot_id].append( (asset, unit, spot(unit)) )
					
		spot_id += 1
		
	# full option generations (pick one for each spot) 
	# need to recursively iterate through all combinations of options
	spot_indices = [0]*len(spot_options)
	i = 0
	#for spot in spot_options:
	#	spot_indices[i] = len(spot_options[i])
		
	options_exhausted = False
	while !options_exhausted:
		# generating option
		option = []
		
		spot_id = 0
		for spot in spot_options:
			swap = spot[spot_indices[spot_id]]
			swapped_asset = swap[0]
			
			asset_match = False
			for spot in option:
				if swapped_asset.id != option(1).id: #asset ID check
					asset_match = True
					
			if !asset_match:
				option.append(spot[spot_indices[spot_id]])
				
		# incrementing index
		spot_indices = increment_indices(spot_indices, spot_options, 0)
		
		options_exhausted = (spot_indices == None)
		
		# evaluate option
		score = score(option)
		if score > best_option_score:
			best_option = option
		# option becomes option from each of the spots, increment index for
		# the 0 index
		# if it's too long for that spot's options reset to 0
		# and chase it up the chain to evaluate all options
		# if that particular asset ID is already in the solution, sub no swap
		# for that case, the feasible solutions will be handled through iteration
		# do nothing if NONE or run out of options for that spot 