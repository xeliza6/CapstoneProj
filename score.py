#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 15:27:25 2017

@author: robmaj12
"""

def score(option):
    # option[i] = (asset_id, unit_from_id, unit_to_id)
    # option[0][0] = asset_id #for option 0
    alpha = 5
    
    scale_uptime = 0.8
    scale_transfer = 0.2 
    score_uptime = 0
    score_transfer = 0
    
    total_transfers = len(option)
    
    unit_surplus = {}
    unit_states = {}
    
    for asset in option:
        asset_id = asset[0]
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
            score_uptime += new_state*alpha*(1 - uptime(unit))
        else:
            score_uptime += alpha*(1 - uptime(unit))
    
    # transfer score
    holes_total = 0
    transfer_num = 0
    
    beta = 3
    
    holes_total = get_holes_total(option)
    tranfer_num = get_tranfer_num(option)
    score_transfer = holes_total/transfer_num - beta*(total_transfers)
    
    return scale_transfer*score_transfer + scale_uptime*score_uptime
  
    
    