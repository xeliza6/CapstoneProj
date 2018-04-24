import json
import oo_simulation
import oo_create_tables
from collections import OrderedDict
import math
import random
from datetime import datetime, timedelta
yal = open("tidytransfers.txt", 'w')
logger = open("transfer_log.txt", 'w')


def get_rand_color():
    letters = '0123456789ABCDEF';
    color = '#'
    for i in range(0, 6):
        color = color + letters[math.floor(random.random() * 16)]
    return color


def make_colors(unit_dict):
    colors = OrderedDict()
    for u in units_dict:
        colors[u] = get_rand_color()
    return colors


def get_transfers_dict(transfers_array):
    global units_dict
    date_format = "%Y-%m-%d"
    clock_zero = datetime.strptime("2018-01-01", date_format)

    # time step will increment every time time stamp changes
    time_step = 0
    time_stamp = int(transfers_array[0][3])
    time_string = (clock_zero+timedelta(days=time_stamp)).strftime("%Y-%m-%d")

    # dictionary holding transfers from unit to itself
    static_transfers = OrderedDict()
    static_transfers[0] = [OrderedDict(), time_string]
    # dictionary holding transfers from one unit to another
    transfers = OrderedDict()
    transfers[0] = [OrderedDict(), time_string]


    for index in range(0, len(transfers_array)):
        t = transfers_array[index]
        # if the system time has changed, transfer the remaining assets in each unit to its current self
        if t[3] != time_stamp:
            for k in unit_ids:
                if units_dict[k][0] == 0:
                    static_transfers[time_step][0][k] = 0.001
                else:
                    static_transfers[time_step][0][k] = units_dict[k][0]
                units_dict[k][0] = units_dict[k][1]
            # then change the time step
            time_step = time_step + 1
            time_stamp = int(t[3])
            time_string = (clock_zero + timedelta(days=time_stamp)).strftime("%Y-%m-%d")
            transfers[time_step] = [OrderedDict(), time_string]
            static_transfers[time_step] = [OrderedDict(), time_string]
        if index == len(transfers_array) - 1:
            for k in unit_ids:
                if units_dict[k][0] == 0:
                    static_transfers[time_step][0][k] = 0.001
                else:
                    static_transfers[time_step][0][k] = units_dict[k][0]
        if t[1] + '-' + t[2] in transfers[time_step][0]:
            transfers[time_step][0][t[1] + '-' + t[2]] = transfers[time_step][0][t[1] + '-' + t[2]] + 1
        else:
            transfers[time_step][0][t[1] + '-' + t[2]] = 1
        if units_dict[t[1]][0] == 0:
            print("attempting to do the following transfer at time step " + str(time_step) + ":")
            print(t)
            print("grabbing from empty unit")
        units_dict[t[1]][0] = units_dict[t[1]][0] - 1
        units_dict[t[1]][1] = units_dict[t[1]][1] - 1
        units_dict[t[2]][1] = units_dict[t[2]][1] + 1
    return static_transfers, transfers, time_step


# print(same_unit_dict)
# for k in units_dict:
#     transfers[time_step][k + '-' + k] = units_dict[k][0]
#     units_dict[k][0] = units_dict[k][1]


units_dict = OrderedDict()
temp_units = oo_create_tables.create_units()
oo_create_tables.create_assets(temp_units)

unit_ids = [k for k in temp_units]
unit_ids.sort()
for u in unit_ids:
    units_dict[u] = temp_units[u].online_asset_count()
# unit_ids.append("MA")
unit_ids.append("EOL")
# units_dict["MA"] = 10
units_dict["EOL"] = 0
# units_dict[0] = unit size before event processing
# units_dict[1] = unit size after event processing
for u in units_dict:
    units_dict[u] = [units_dict[u], units_dict[u]]

transfer_data = oo_simulation.get_sankey_data()
transfer_data = transfer_data[:1000]

same_unit_dict, transfers, time_step = get_transfers_dict(transfer_data)

links = []
nodes = []

for k in unit_ids:
    for time in transfers:
        assets = same_unit_dict[time][0][k]
        tooltip_str = k + '-->' + k + '<br/>Assets: ' + str(assets) + '<br/>' + str(transfers[time][1])
        yal.write(k + str(time) + "|" + k + str(time + 1) + "|" + str(assets) + '|' + tooltip_str + "\n")
for time in transfers:
    for transfer in transfers[time][0]:
        if transfers[time][0][transfer] != 0:
            unitf = transfer.split("-")[0]
            unitt = transfer.split("-")[1]
            assets = transfers[time][0][transfer]
            tooltip_str = unitf + '-->' + unitt + '<br/>Assets: ' + str(assets) + '<br/>' + str(transfers[time][1])
            yal.write(
                unitf + str(time) + "|" + unitt + str(time + 1) + "|" + str(assets) + '|' + tooltip_str + "\n")
for f in transfer_data:
    logger.write(str(f) + '\n')
for t in transfers:
    logger.write(str(transfers[t]) + '\n')
colors = make_colors(units_dict)
for c in colors:
    yal.write(c + ":" + colors[c] + ',')

yal.write(str(time_step))
