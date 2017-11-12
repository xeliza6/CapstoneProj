#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 15:27:25 2017

@author: robmaj12
"""

def score(option, holes):
    # option[i] = (asset_id, unit_from_id, unit_to_id)
    # option[0][0] = asset_id #for option 0
    alpha = 5
    
    scale_uptime = 0.8
    scale_transfer = 0.2

	cur.execute("SELECT * FROM unit_state")
	old_unit_states = cur.fetchall()
	
	
# INITIALIZING 	
    score_uptime = 0
    score_transfer = 0
    
    total_transfers = len(option)
    
	
	unit_surplus = {}
    unit_states = {}
	unit_downtime = {}
	
	for unit in old_unit_states:
		unit_surplus[unit[0]] = unit[3] - unit[4] # positive if excess, negative if shortage
		unit_states[unit[0]] = math.signum(unit_surplus[unit[0]]
		unit_downtime[unit[0]] = unit[2]/system_clock
		

    # states are 1 if surplus, 0 if exact, -1 if offline
	# querying unit surplus & states
	
	# uptime/downtime changes
    for asset in option:
        asset_id = asset[0]
        
		if asset_id != None:
			unit_id_from = asset[1]
			unit_id_to = asset[2]
			
			unit_surplus[unit_id_from] -= 1
			unit_surplus[unit_id_to] += 1
        
    unit_changes = {}
    
    for unit_id, val in unit_states:
        # positive if online, negative if offline
        if math.signum(unit_surplus[unit_id]) != unit_states[unit_id]:
            unit_changes[unit_id] = math.signum(unit_surplus[unit_id])

    for unit_id, new_state in units_changes:
        if new_state != 0:
            score_uptime += new_state*alpha*unit_downtime[unit_id]
        else:
            score_uptime += alpha*unit_downtime[unit_id]
    
    # transfer score
    holes_total = 0
    transfer_num = 0
    
    beta = 0.3
    
    holes_total = len(holes)
    tranfer_num =  len(option)
    score_transfer = transfer_num/holes_total - beta*(total_system_transfers)
    
    return scale_transfer*score_transfer + scale_uptime*score_uptime
  
    
    