import json
import oo_simulation
import oo_create_tables
from collections import OrderedDict
import math
import random

def get_rand_color():
    letters = '0123456789ABCDEF';
    color = '#'
    for i in range(0,6):
        color = color + letters[math.floor(random.random()*16)]
    return color

yal = open("tidytransfers.txt", 'w')
logger = open("transfer_log.txt", 'w')

time_stamps = []
transfers = OrderedDict()
same_unit_dict = OrderedDict()
units_dict = OrderedDict()
colors = OrderedDict()
temp_units = oo_create_tables.create_units()
oo_create_tables.create_assets(temp_units)

unit_ids = [k for k in temp_units]
unit_ids.sort()
for u in unit_ids:
    units_dict[u] = temp_units[u].online_asset_count()
unit_ids.append("MA")
unit_ids.append("EOL")
units_dict["MA"] = 10
units_dict["EOL"] = 10

transfer_ids = []
for u1 in unit_ids:
    for u2 in unit_ids:
        transfer_ids.append(u1+'-'+u2)
for u in units_dict:
    colors[u] = get_rand_color()

#transfer_data = [[23,"B","A",14,2],[32, "A","C",14,1],[23,"B","A",14,2],[25,"B","A",17,6]]
transfer_data = oo_simulation.get_sankey_data()
transfer_data = transfer_data[:3000]

time_step = 0
time_stamp = 0
transfers[0]=OrderedDict()
same_unit_dict[0] = OrderedDict()
for u in units_dict:
    units_dict[u] = [units_dict[u],units_dict[u]]
for index in range(0,len(transfer_data)):
    t= transfer_data[index]
    # if the system time has changed, transfer the remaining assets in each unit to its current self
    if t[3]!=time_stamp:
        for k in unit_ids:
            if units_dict[k][0]<=0:
                same_unit_dict[time_step][k] = 0.001
            else:
                same_unit_dict[time_step][k] = units_dict[k][0]
            units_dict[k][0]= units_dict[k][1]
        # then change the time step
        time_step = time_step + 1
        time_stamp = t[3]
        transfers[time_step] = OrderedDict()
        same_unit_dict[time_step] = OrderedDict()
    if index == len(transfer_data)-1:
        for k in unit_ids:
            if units_dict[k][0] <= 0:
                same_unit_dict[time_step][k] = 0.001
            else:
                same_unit_dict[time_step][k] = units_dict[k][0]
    if t[1]+'-'+t[2] in transfers[time_step]:
        transfers[time_step][t[1]+'-'+t[2]] = transfers[time_step][t[1]+'-'+t[2]] + 1
    else:
        transfers[time_step][t[1]+'-'+t[2]] = 1
    units_dict[t[1]][0] = units_dict[t[1]][0] - 1
    units_dict[t[1]][1] = units_dict[t[1]][1] - 1

    units_dict[t[2]][1] = units_dict[t[2]][1] + 1
print(same_unit_dict)
for k in units_dict:
    transfers[time_step][k + '-' + k] = units_dict[k][0]
    units_dict[k][0] = units_dict[k][1]

links=[]
nodes=[]
# for time in transfers:
#     for k in same_unit_dict[time]:
#         yal.write(k + str(time) + "|" + k + str(time + 1) + "|" + str(same_unit_dict[time][k]) + "\n")
# for time in transfers:
for k in unit_ids:
    for time in transfers:
            yal.write(k + str(time) + "|" + k + str(time + 1) + "|" + str(same_unit_dict[time][k]) + "\n")
for time in transfers:
    for transfer in transfers[time]:
        if transfers[time][transfer]!=0:
            unitf = transfer.split("-")[0]
            unitt = transfer.split("-")[1]
            yal.write(unitf+str(time) + "|" + unitt+str(time+1) + "|"+ str(transfers[time][transfer]) + "\n")
for f in transfer_data:
    logger.write(str(f) + '\n')
for t in transfers:
    logger.write(str(transfers[t])+'\n')

for c in colors:
    yal.write(c+":"+colors[c]+',')

print(same_unit_dict)