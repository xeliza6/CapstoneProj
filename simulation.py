import psycopg2
import math
import random
import imp
import create_tables
from datetime import datetime, timedelta
import matplotlib as plt
date_format = "%Y-%m-%d"

create_tables.main()

try:
    conn = psycopg2.connect("dbname='scheduling' user='postgres' host='localhost' password='mac.gpotat0'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

clock_zero = datetime.strptime("2018-01-01", date_format)
logger = open("transfer_log.txt", 'w')
cap = 7000
maintenance_lim = 3500
maintenance = 180
system_clock = 0
old_system_clock = 0
baseline_uptime = 0
total_system_uptime = 0
total_system_transfers = 0
transfers_array = []
uptimes_array = []
time_array = []
end_condition = False

cur.execute("SELECT * FROM unit_state")
unit_ids = []
temp = cur.fetchall()
for unit in temp:
    unit_ids.append(unit[0])


def initialize_unit_states():
    # initializing unit states
    for unit in unit_ids:
        cur.execute("SELECT id FROM asset_states WHERE curr_unit = '" + unit + "'")
        cur.execute(
            "UPDATE unit_state SET assets = " + str(len(cur.fetchall())) + ", state = 1 WHERE unit_id = '" + unit + "'")
        cur.execute("SELECT asset_demand FROM unit" + unit + " WHERE id = 1")
        cur.execute(
            "UPDATE unit_state SET assets_required = " + str(cur.fetchall()[0][0]) + " WHERE unit_id = '" + unit + "'")

    cur.execute("SELECT * FROM unit_state")
    # print(cur.fetchall())

# ----------------------------------------DETECTING NEXT EVENT-------------------------------------------

def set_events():
    cur.execute("TRUNCATE TABLE events")
    for unit in unit_ids:
        find_unit_event(unit)


def find_unit_event(unit):
    cur.execute("SELECT state,assets, assets_required FROM unit_state WHERE unit_id = '" + unit + "'")
    line = cur.fetchone()
    state = line[0]

    unit_table = 'unit' + unit
    cur.execute(
        "SELECT start_date, end_date, asset_demand, util_type, rate_unit, rate_value FROM " + unit_table +
        " LEFT OUTER JOIN phases ON " + unit_table + ".phase = phases.phase_id WHERE " + unit_table + ".id = " + str(
            state))

    phase = cur.fetchone()
    cur.execute("SELECT * FROM asset_states WHERE curr_unit = '" + unit + "'")
    assets = cur.fetchall()

    for asset in assets:
        find_asset_event(asset, phase)

    cur.execute("SELECT * FROM unit" + unit + " WHERE id > " + str(state))

    next_phase = cur.fetchone()
    # print(next_phase)
    # print(unit)

    if next_phase != None:
        cur.execute("INSERT INTO events(id, object_type, event_date, event_type, new_required)"
                    "VALUES ('" + unit + "', 'unit'," + str(next_phase[2]) + ",'PC', " + str(next_phase[4]) + ")")


def find_asset_event(asset, phase):
    curr_util = 0
    if asset[4] == 'O':
        curr_util = asset[3]
    if asset[4] == 'M':
        curr_util = asset[5]
    maintenance_checkpoint = int(curr_util / maintenance_lim) * maintenance_lim + maintenance_lim
    maintenance_checkpoint2 = 180
    end_date = phase[1]
    day_diff = end_date - system_clock
    if phase[4] == 'perAsset_PerDay':
        hrs_per_day = int(phase[5])
    else:
        hrs_per_day = phase[5] / phase[2]
    added_hours = day_diff * hrs_per_day
    temp_curr_util = curr_util + added_hours

    # If asset is not in maintenance
    if asset[4] == 'O':
        # Check if asset hits maintenance
        if asset[5] == -1:
            maintenance_checkpoint = maintenance_checkpoint + maintenance_lim
            cur.execute("UPDATE asset_states SET maintenance = 0")
        if temp_curr_util >= maintenance_checkpoint:

            remaining = int((maintenance_checkpoint - curr_util) / hrs_per_day)
            # print(remaining)
            exec_date = system_clock + remaining
            # print("Asset " + asset_id + " in maintenance on "+ str(exec_date))
            command = """
                            INSERT INTO events (id, object_type, event_date, event_type)
                            VALUES(""" + str(asset[0]) + ", 'asset'," + str(exec_date) + ", 'M')"

            cur.execute(command)
        # Check if asset hits EOL
        if curr_util >= cap:
            remaining = int((cap - curr_util) / hrs_per_day)
            # print(remaining)
            exec_date = system_clock + remaining
            command = "INSERT INTO events (id, object_type, event_date, event_type)  VALUES(" + str(
                asset[0]) + ", 'asset'," + str(exec_date) + ", 'EOL')"
            cur.execute(command)
            # print("Asset " + str(asset[0]) + " EOL ")


    # If asset was in maintenance
    else:
        # Check if asset comes back online
        if temp_curr_util >= maintenance_checkpoint2:
            remaining = int((maintenance_checkpoint2 - curr_util) / hrs_per_day)
            # print(remaining)
            exec_date = system_clock + remaining
            # print("Asset " + asset_id + " in maintenance on "+ str(exec_date))
            command = """
                INSERT INTO events (id, object_type, event_date, event_type)
                VALUES(""" + str(asset[0]) + ", 'asset'," + str(
                exec_date) + ", 'EM')"

            cur.execute(command)


# Find next event
# Update system clock to next event
def find_next_event():
    global system_clock
    global end_condition
    cur.execute("SELECT * FROM events")
    events = cur.fetchall()
    if len(events)==0:
        end_condition = True
        return
    nearest = events[0]
    for event in events:
        if event[2] <= nearest[2]:
            nearest = event
    print("------------------------------------ next event is: " + str(nearest))
    logger.write("\nAt " + str(datetime.strftime(clock_zero + timedelta(days=nearest[2]), date_format)) + ": " + str(
        nearest[1]) + " " + str(nearest[0]) + " " + str(nearest[3]) + "\n")
    system_clock = nearest[2]
    event_id = nearest[0]
    # print("next event is: " + str(nearest))
    # print(system_clock)

    cur.execute("DELETE FROM events WHERE id = '" + event_id + "'")

    # Update asset state
    # Update unit_state.assets
    # Update next event in events table
    if nearest[1] == 'asset':
        update_assets()

        cur.execute("SELECT * FROM asset_states WHERE id = '" + event_id + "'")
        asset = cur.fetchone()
        if nearest[3] == "M":
            cur.execute("UPDATE asset_states SET state = 'M' WHERE id = " + str(event_id))
            cur.execute("SELECT curr_unit FROM asset_states")
            curr_unit = cur.fetchone()[0]
            cur.execute("UPDATE unit_state SET assets = unit_state.assets-1 WHERE unit_id = '" + curr_unit + "'")

        elif nearest[3] == 'EOL':
            cur.execute("UPDATE asset_states SET state = 'EOL', maintenance =0 WHERE id = " + str(event_id))
            cur.execute("SELECT curr_unit FROM asset_states")
            curr_unit = cur.fetchone()[0]
            cur.execute(
                "UPDATE unit_state SET assets = unit_state.assets-1, curr_unit = 'n/a' WHERE unit_id = '" + curr_unit + "'")

        elif nearest[3] == "EM":
            cur.execute("UPDATE asset_states SET state = 'O', maintenance = -1 WHERE id = " + event_id)
            cur.execute("SELECT curr_unit FROM asset_states")
            curr_unit = cur.fetchone()[0]
            cur.execute("UPDATE unit_state SET assets = unit_state.assets+1 WHERE unit_id = '" + curr_unit + "'")


    # Update unit state
    # Update unit_state.asset_requirement
    # Update next event in events table
    elif nearest[1] == 'unit':
        cur.execute("UPDATE unit_state SET state = unit_state.state+1, assets_required = " + str(
            nearest[4]) + " WHERE unit_id = '" + event_id + "'")
        update_assets()
        find_unit_event(event_id)

# -------------------------------------------UPDATING STATE-----------------------------------------------
def update_assets():
    day_diff = system_clock - old_system_clock
    #print("DAY DIFF: " + str(system_clock) + " - " + str(old_system_clock) + " = " + str(day_diff))
    for unit in unit_ids:
        cur.execute("SELECT state, assets, assets_required FROM unit_state WHERE unit_id = '" + unit + "'")
        line = cur.fetchone()
        if line[1] >= line[2]:
            state = line[0]
            table = 'unit' + unit
            cur.execute(
                "SELECT phase, asset_demand, rate_unit, rate_value FROM unit" + unit + " RIGHT OUTER JOIN phases ON phases.phase_id = " + table + ".phase WHERE " + table + ".id = " + str(
                    state))
            phase = cur.fetchone()

            if phase[2] == 'perAsset_PerDay':
                hrs_per_day = int(phase[3])
            else:
                hrs_per_day = phase[3] / phase[1]
            added_hours = day_diff * hrs_per_day
            cur.execute("UPDATE asset_states SET curr_util_value = curr_util_value + " + str(
                added_hours) + " WHERE curr_unit = '" + unit + "' AND state = 'O'")
            cur.execute("UPDATE asset_states SET maintenance = maintenance + " + str(
                added_hours) + " WHERE curr_unit = '" + unit + "' AND state = 'M'")


# def update_state():
#     update_assets()

# # Updating asset_states table
# def update_assets():
#     for unit in unit_ids:
#         table = 'unit' + unit
#         cur.execute("SELECT * FROM "+ table  + " LEFT OUTER JOIN phases ON "+ table + ".phase = phases.phase_id")
#         schedule = cur.fetchall()
#         # print(schedule)
#         cur.execute("SELECT * FROM unit_state WHERE unit_id ='" +unit + "'")
#         state = cur.fetchone()
#         assets_in_unit = state[3]
#         state = state[1]
#
#         added_time = 0
#         for phase in schedule:
#             if phase[0] == state:
#                 break
#             elif phase[0] > state:
#                 print("state_id is greater than state, this should not have happened")
#             else:
#                 if phase[7] == "perUnit_perDay" :
#                     per_unit = phase[8]/assets_in_unit
#                     added_time += (phase[3]- phase[2])*per_unit
#                 else:
#                     added_time += (phase[3]-phase[2])*phase[8]
#
#         # print("ADDED TIME " + str(added_time))
#         cur.execute("UPDATE asset_states SET curr_util_value = asset_states.curr_util_value + " + str(added_time) + " WHERE curr_unit = '" + unit + "'")
#

def transfer(asset, unit_a, unit_b):
    global total_system_transfers
    # print("transfering: " + str(asset[0]) + unit_a + unit_b)
    asset_id = str(asset[0])
    cur.execute("UPDATE asset_states SET curr_unit = '" + unit_b + "' WHERE id = " + asset_id)
    cur.execute("UPDATE unit_state SET assets = unit_state.assets-1 WHERE unit_id = '" + unit_a + "'")
    cur.execute("UPDATE unit_state SET assets = unit_state.assets+1 WHERE unit_id = '" + unit_b + "'")
    total_system_transfers +=1



# ------------------------------------OPTION GENERATION AND SCORING-------------------------------------------

def signum(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def increment_index(indices, options, rank_depth, incr_index):
    threshold = min(rank_depth, len(options[incr_index]))
    if (indices[incr_index] + 1) < threshold:
        indices[incr_index] += 1
        return indices
    elif (indices[incr_index] + 1) == threshold:
        if (incr_index + 1) == len(indices):
            return None
        indices[incr_index] = 0
        return increment_index(indices, options, rank_depth, incr_index + 1)


def get_rand_option(options):
    indices = [0] * len(options)
    i = 0
    for spot, spot_options in options.items():
        indices[i] = random.randint(0, len(spot_options) - 1)
        i += 1

    return indices


def get_ranked_options(all_options, num_spots, rank_depth):

    # 2D array representing best options per spot (going to length n)
    ranked_options = [[0 for x in range(num_spots)] for y in range(rank_depth)]

    # for each spot
    for i in range(num_spots):
        spot_options = all_options[i]
        best_option_ids = [0]*rank_depth

        best_option_score = 0
        spot_depth = min(rank_depth, len(spot_options))

        for j in range(len(spot_options)):
            option = spot_options[j]
            if option is not None:
                asset_id = option[0][0]
                unit_id_from = option[1]
                unit_id_to = option[2]

                cur.execute("SELECT curr_util_value FROM asset_states WHERE id = " + str(asset_id))
                pct_life_remaining = float(cap - cur.fetchall()[0][0]) / float(cap)
                unit_from_priority = get_phase_priority(unit_id_from)
                unit_to_priority = get_phase_priority(unit_id_to)

                if unit_from_priority == 0:
                    priority_score = 0
                    priority_gate = 0
                else:
                    priority_score = (unit_to_priority - unit_from_priority) / 10.0
                    priority_gate = 1

                cur.execute("SELECT downtime FROM unit_state WHERE unit_id = '" + unit_id_from + "'")
                unit_from_uptime = 1 - (cur.fetchall()[0][0] / float(system_clock))

                priority_weight = 0.4
                uptime_weight = 0.4
                lifetime_weight = 0.2

                option_score = priority_gate*(priority_weight*priority_score + uptime_weight*unit_from_uptime + lifetime_weight*pct_life_remaining)

            else:
                option_score = 0
            if option_score > best_option_score:
                for k in range(rank_depth - 1):
                    best_option_ids[rank_depth - 1 - k] = best_option_ids[rank_depth - k - 2]

                best_option_ids[0] = j
                best_option_score = option_score

        # storing best spots
        for j in range(spot_depth):
            ranked_options[j][i] = best_option_ids[j]

    best_options = {}
    for i in range(num_spots):

        best_options[i] = [None]

        for j in range(rank_depth):
            ranked_option = ranked_options[j][i]
            best_options[i].append(all_options[i][ranked_option])

    # each option is a list of tuples of (Asset #, unit from ID, unit to ID)
    # so ranked_options will be a list of list of tuples
    return best_options


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

                for asset in assets_in_unit(spot_unit):
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


    # SWITCHING TO RANKED OPTIONS HERE
    all_options = spot_options

    rank_depth = 5
    spot_options = get_ranked_options(spot_options, len(spot_indices), rank_depth)

    options_exhausted = False
    options_evaluated = 0
    while not options_exhausted and options_evaluated < 200:
        # options_evaluated += 1
        # generating option
        option = []
        option_ids = [0] * len(spot_indices)
        for spot_id, spot in spot_options.items():
            if spot[spot_indices[spot_id]] is not None:
                swap = spot[spot_indices[spot_id]]  # deciding which "option" to pick for this spot
                swapped_asset = swap[0]  # asset ID being swapped

                asset_match = False
                for opt_spot in option:
                    if swapped_asset[0] == opt_spot[0][0]:  # asset ID check
                        asset_match = True

                if not asset_match:
                    option.append(spot[spot_indices[spot_id]])  # may pass None, None indicates no swap
                    option_ids[spot_id] = spot_indices[spot_id]
                else:
                    spot_empty = True
                    i = 0
                    while spot_indices[spot_id] + i + 1 < min(rank_depth, len(spot_options[spot_id])) and spot_empty:
                        i += 1
                        if spot[spot_indices[spot_id] + i] is not None:
                            swap = spot[spot_indices[spot_id] + i]  # deciding which "option" to pick for this spot
                            swapped_asset = swap[0]  # asset ID being swapped

                            asset_match = False
                            for opt_spot in option:
                                if swapped_asset[0] == opt_spot[0][0]:  # asset ID check
                                    asset_match = True
                            if not asset_match:
                                option.append(spot[spot_indices[spot_id] + i])
                                option_ids[spot_id] = spot_indices[spot_id] + i
                                spot_empty = False

        # incrementing index

        # USE WHEN SWITCHING OFF OF RANDOMIZATION
        option_depth = 3
        spot_indices = increment_index(spot_indices, spot_options, option_depth, 0)
        #print(option_ids)
        # USE FOR RANDOM SELECTION
        #spot_indices = get_rand_option(spot_options)

        # print(spot_indices)

        options_exhausted = (spot_indices is None)

        # evaluate option
        score = score_option(option, empty_spots)
        if score > best_option_score:
            best_option = option
            best_option_score = score

    return best_option, best_option_score
    # option becomes option from each of the spots, increment index for
    # the 0 index
    # if it's too long for that spot's options reset to 0
    # and chase it up the chain to evaluate all options
    # if that particular asset ID is already in the solution, sub no swap
    # for that case, the feasible solutions will be handled through iteration
    # do nothing if NONE or run out of options for that spot


# Returns phase priority for a unit's current state
def get_phase_priority(unit_id):
    cur.execute("SELECT state FROM unit_state WHERE unit_id = '" + unit_id + "'" )
    curr_phase_status = str(cur.fetchall()[0][0])
    cur.execute("SELECT phase FROM unit" + unit_id + " WHERE id = " + curr_phase_status)
    phase = str(cur.fetchall()[0][0])
    cur.execute("SELECT priority from phase_priority WHERE phase_id = '" + phase + "'")
    return cur.fetchall()[0][0]


def score_option(option, holes):
    # option[i] = (asset_id, unit_from_id, unit_to_id)
    # option[0][0] = asset_id #for option 0
    alpha = 10

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
        unit_downtime[unit[0]] = unit[2] / float(system_clock)

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

        phase_priority = get_phase_priority(unit_id)

        if phase_priority == 0:
            phase_weight = 10
        else:
            phase_weight = (10 - phase_priority) * 0.5

        if new_state != 0:
            score_uptime += phase_weight*new_state * alpha * unit_downtime[unit_id]
        else:
            score_uptime += phase_weight*alpha * unit_downtime[unit_id]

    # transfer score
    beta = 0.005
    holes_total = len(holes)
    transfer_num = len(option)
    score_transfer = transfer_num / holes_total - beta * (total_system_transfers)
    return scale_transfer * score_transfer + scale_uptime * score_uptime


# ---------------------------------------------HELPER METHODS-------------------------------------------------

def assets_in_unit(unit_id):
    cur.execute("SELECT * FROM asset_states WHERE curr_unit = '" + unit_id + "' AND state = 'O'")
    return cur.fetchall()


def calculate_downtime():
    global total_system_uptime
    cur.execute("SELECT * FROM unit_state")
    units = cur.fetchall()
    for unit in units:
        period_downtime = int((system_clock - old_system_clock)*max(0, ((unit[4] - unit[3])/float(unit[4]))))
        cur.execute("UPDATE unit_state SET downtime = unit_state.downtime +" + str(
            period_downtime) + " WHERE unit_id = '" + unit[0] + "'")
        total_system_uptime = total_system_uptime - period_downtime


def get_holes():
    cur.execute("SELECT * FROM unit_state WHERE assets < assets_required")
    stuff = cur.fetchall()
    holes_tuple = []
    for s in stuff:
        holes_tuple.append((s[0], s[5]))
    return holes_tuple


def calculate_average_uptime():
    global transfers_array
    global uptimes_array
    global time_array
    uptimes_array.append(total_system_uptime/len(unit_ids))
    transfers_array.append(total_system_transfers)
    time_array.append(system_clock)


if __name__ == '__main__':
    old_system_clock = 0

    initialize_unit_states()

    while end_condition is False:
        calculate_downtime()
        old_system_clock = system_clock
        calculate_average_uptime()
        set_events()
        find_next_event()
        boom = generate_options(get_holes())
        if boom[0] is not None:
            for b in boom[0]:
                transfer(b[0], b[1], b[2])
                logger.write("    Asset " + str(b[0][0]) + " was transferred from " + b[1] + " to " + b[2] + ", action score = " + str(boom[1]) + "\n")

        else:
            logger.write("    No action was taken, action score = " + str(boom[1]) + "\n")
        day_diff = system_clock - old_system_clock
        if day_diff < 0:
            break
        logger.write("\n-----------------\n")
    print("Exiting Simulation")
    logger.write("\nTotal Transfers: " + str(total_system_transfers))

    cur.execute("select * from unit_state")
    unit_states = cur.fetchall()

    avg_uptime = 0

    for unit in unit_states:
        u_id = unit[0]
        uptime = 100 - 100*(float(unit[2]) / float(system_clock))
        logger.write("\nUnit " + str(u_id) + " uptime is " + str(uptime) + "%")
        avg_uptime += uptime

    logger.write("\nAverage System Uptime is " + str(avg_uptime/len(unit_states)) + "%")



logger.close()
cur.close()
conn.commit()
