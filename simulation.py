

import psycopg2
import math
import random
from datetime import datetime, timedelta
date_format = "%Y-%m-%d"

try:
    conn = psycopg2.connect("dbname='scheduling' user='postgres' host='localhost' password='pass'")
except:
    print ("I am unable to connect to the database")

cur = conn.cursor()

cap = 12000
maintenance_lim = 8000
maintenance = 180

system_clock = 0
old_system_clock = 0

total_system_transfers = 0

cur.execute("SELECT * FROM unit_state")
unit_ids = []
temp = cur.fetchall()
for unit in temp:
    unit_ids.append(unit[0])
# go through each asset and find the next event


def initialize_unit_states():
    for unit in unit_ids:
        cur.execute("SELECT id FROM asset_states WHERE curr_unit = '"+ unit + "'")
        cur.execute("UPDATE unit_state SET assets = " + str(len(cur.fetchall())) + ", state = 1 WHERE unit_id = '" + unit + "'")
        cur.execute("SELECT asset_demand FROM unit" + unit + " WHERE id = 1")
        cur.execute("UPDATE unit_state SET assets_required = " + str(cur.fetchall()[0][0]) + " WHERE unit_id = '" + unit + "'")

    cur.execute("SELECT * FROM unit_state")
    print(cur.fetchall())


def asset_milestone():
    cur.execute("SELECT * FROM asset_states;")
    asset_data = cur.fetchall()
    # looping through assets
    for asset in asset_data:
        asset_id = str(asset[0])
        curr_util = asset[4]
        curr_unit = asset[3]
        maintenance_checkpoint = int(curr_util/maintenance_lim)*maintenance_lim + maintenance_lim
        #print(curr_unit)
        cur.execute("SELECT * FROM unit" + curr_unit)
        all_transfers = cur.fetchall()
        #finding the next event for the asset
        for transfer in all_transfers:
            start_time = transfer[2]
            end_time = transfer[3]
            day_diff = end_time-start_time
            # print(str(day_diff))
            cur.execute("""SELECT * FROM phases
             WHERE phase_id = '""" + transfer[1] + "'")
            phase = cur.fetchone()
            # print(phase)
            if phase[2] == 'perAsset_PerDay':
                hrs_per_day = int(phase[3])
            else:
                hrs_per_day = phase[3]/transfer[4]

            added_hours = day_diff * hrs_per_day
            temp_curr_util = curr_util + added_hours
            # record the events appropriately in the event table
            # update the state of the asset in the asset table
            # freeze the data
            if temp_curr_util >= maintenance_checkpoint:

                remaining = int((maintenance_checkpoint - curr_util)/hrs_per_day)
                # print(remaining)
                exec_date = start_time+ remaining
                # print("Asset " + asset_id + " in maintenance on "+ str(exec_date))
                command = """
                                INSERT INTO "events" (id, object_type, event_date, event_type)
                                VALUES('""" + asset_id + "', 'asset',"+ str(exec_date) + ", 'maintenance')"

                cur.execute(command)
                break

            # elif curr_util >= cap:
            #     print("asset " + asset_id + "EOL")
            #     command = """
            #             INSERT INTO "events" (id, object_type, event_date, event_type)
            #             VALUES('""" + str(asset[0]) + """', 'asset', 'placeholder', 'EOL')
            #             """
            #     cur.execute(command)
            #     print("Asset " + asset_id + " EOL ")

                # break
            else:
                curr_util = temp_curr_util
    update_state()

def update_state():
    # calculate downtime up until current clock time
    cur.execute("SELECT * FROM unit_state")
    unit_states = cur.fetchall()
    for state in unit_states:
        if state[3]<state[4]:
            cur.execute("UPDATE unit_state SET downtime = " + str(system_clock - old_system_clock) + " WHERE unit_id ='" +state[0] + "'")

    find_next_event()
    for unit in unit_ids:
        cur.execute("SELECT * FROM unit" + unit)
        unit_schedule = cur.fetchall()
        for time in unit_schedule:
            if time[3] > system_clock:
                curr_state = time[0]
                assets_needed = time[4]
                assets_in = len(assets_in_unit(unit))
                cur.execute(
                    """UPDATE unit_state
                    SET state = """ + str(curr_state) + """, assets =  """+ str(assets_in) +""", assets_required ="""+ str(assets_needed)+"""
                    WHERE unit_id = '""" + unit + "'")




def find_next_event():
    global system_clock
    cur.execute("SELECT * FROM events")
    events = cur.fetchall()
    nearest = events[0]
    for event in events:
        if event[2]<nearest[2]:
            nearest = event
    system_clock = nearest[2]
    if nearest[3] == "maintenance":
        cur.execute("UPDATE asset_states SET state = 'maintenance' WHERE id = " + nearest[0])


def assets_in_unit(unit_id):
    cur.execute("SELECT * FROM asset_states WHERE curr_unit = '" + unit_id + "' AND state = 'online'" )
    return cur.fetchall()

def get_holes():
    cur.execute("SELECT * FROM unit_state WHERE assets < assets_required")
    stuff = cur.fetchall()
    holes_tuple = []
    for s in stuff:
        holes_tuple.append((s[0],s[5]))
    return holes_tuple

def update_assets():
    for unit in unit_ids:
        table = 'unit' + unit
        cur.execute("SELECT * FROM "+ table  + " LEFT OUTER JOIN phases ON "+ table + ".phase = phases.phase_id")
        schedule = cur.fetchall()
        print(schedule)
        cur.execute("SELECT * FROM unit_state WHERE unit_id ='" +unit + "'")
        state = cur.fetchone()
        assets_in_unit = state[3]
        state = state[1]

        temp_clock = system_clock
        added_time = 0
        for phase in schedule:
            if phase[0] == state:
                break
            elif phase[0] > state:
                print("state_id is greater than state, this should not have happened")
            else:
                if phase[7] == "perUnit_perDay" :
                    per_unit = phase[8]/assets_in_unit
                    added_time += (phase[3]- phase[2])*per_unit
                else:
                    added_time += (phase[3]-phase[2])*phase[8]
            print("ADDED TIME " + str(added_time))
            cur.execute("UPDATE asset_states SET curr_util_value = asset_states.curr_util_value + " + str(added_time) + " WHERE curr_unit = '" + unit + "'")



def signum(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1






# CMDA capstone option generation / scoring function


def increment_index(indices, options, incr_index):
    if (indices[incr_index] + 1) < len(options[incr_index]):
        indices[incr_index] += 1
        return indices
    elif (indices[incr_index] + 1) == len(options[incr_index]):
        if(incr_index + 1) == len(indices):
            return None
        indices[incr_index] = 0
        return increment_index(indices, options, incr_index + 1)

def get_rand_option(options):
    indices = [0]*len(options)
    i = 0
    for spot, spot_options in options.items():
        indices[i] = random.randint(0, len(spot_options))
        i += 1

    return indices

# arguments passed in should be a list of tuplets of shortages
# of form (unit, asset type)
def generate_options(empty_spots):
    best_option = None
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
        # spot is a tuple of unit, and asset type
        spot_options[spot_id] = [None]

        unit_list = unit_ids
        for spot_unit in unit_list:

            if spot_unit != spot[0]:

                for asset in assets_in_unit(unit):
                    # TODO: implement this conditional when we have multiple asset types
                    # if asset.type == spot(asset_type):
                    # each alternative stored as a triplet
                    # form (asset, unit from, unit to)
                    # spot_options[spot_id].append( (asset, unit, spot[0]) )
                    # TODO: remove this line once the above TODO is taken care of
                    spot_options[spot_id].append((asset, spot_unit, spot[0]))
        spot_id += 1

    # full option generations (pick one for each spot)
    # need to recursively iterate through all combinations of options
    spot_indices = [0] * len(spot_options)
    i = 0
    # for spot in spot_options:
    # 	spot_indices[i] = len(spot_options[i])

    options_exhausted = False
    options_evaluated = 0
    while not options_exhausted and options_evaluated < 10000:
        options_evaluated += 1
        # generating option
        option = []

        for spot_id, spot in spot_options.items():
            if spot[spot_indices[spot_id]] is not None:
                swap = spot[spot_indices[spot_id]]  # deciding which "option" to pick for this spot
                swapped_asset = swap[0]  # asset ID being swapped

                asset_match = False
                for opt_spot in option:
                    if swapped_asset != opt_spot[0]:  # asset ID check
                        asset_match = True

                if not asset_match:
                    option.append(spot[spot_indices[spot_id]])  # may pass None, None indicates no swap

        # incrementing index

        ## REPLACE WHEN SWITCHING OFF OF RANDOMIZATION
        ## spot_indices = increment_index(spot_indices, spot_options, 0)

        ## USE FOR RANDOM SELECTION
        spot_indices = get_rand_option(spot_options)

        print(spot_indices)

        options_exhausted = (spot_indices is None)

        # evaluate option
        score = score_option(option, empty_spots)
        if score > best_option_score:
            best_option = option
            best_option_score = score
    print("OPTION REPORTING OPTION REPORTING OPTION REPORTING")
    print(best_option)
    return best_option
    # option becomes option from each of the spots, increment index for
    # the 0 index
    # if it's too long for that spot's options reset to 0
    # and chase it up the chain to evaluate all options
    # if that particular asset ID is already in the solution, sub no swap
    # for that case, the feasible solutions will be handled through iteration
    # do nothing if NONE or run out of options for that spot


def score_option(option, holes):
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
        unit_surplus[unit[0]] = unit[3] - unit[4]  # positive if excess, negative if shortage
        unit_states[unit[0]] = signum(unit_surplus[unit[0]])
        unit_downtime[unit[0]] = unit[2] / system_clock

    # states are 1 if surplus, 0 if exact, -1 if offline
    # querying unit surplus & states

    # uptime/downtime changes
    for asset in option:
        asset_id = asset[0]

        if asset_id is not None:
            unit_id_from = asset[1]
            unit_id_to = asset[2]

            unit_surplus[unit_id_from] -= 1
            unit_surplus[unit_id_to] += 1

    unit_changes = {}

    for unit_id, val in unit_states.items():
    # positive if online, negative if offline
        if signum(unit_surplus[unit_id]) != unit_states[unit_id]:
            unit_changes[unit_id] = signum(unit_surplus[unit_id])

    for unit_id, new_state in unit_changes.items():
        if new_state != 0:
            score_uptime += new_state * alpha * unit_downtime[unit_id]
        else:
            score_uptime += alpha * unit_downtime[unit_id]

    # transfer score
    beta = 0.3

    holes_total = len(holes)
    transfer_num = len(option)
    score_transfer = transfer_num / holes_total - beta * (total_system_transfers)
    return scale_transfer * score_transfer + scale_uptime * score_uptime


if __name__ == '__main__':
    initialize_unit_states()
    asset_milestone()
    update_state()
    update_assets()
    generate_options(get_holes())

a = 4
cur.close()
conn.commit()
