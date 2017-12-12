import psycopg2
import math
import random
import imp
import create_tables
from datetime import datetime, timedelta
import matplotlib as plt
date_format = "%Y-%m-%d"
imp.reload(create_tables)
create_tables.main()

try:
    conn = psycopg2.connect("dbname='scheduling' user='postgres' host='localhost' password='pass'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()


data_file_dict = {}

clock_zero = datetime.strptime("2018-01-01", date_format)
logger = open("transfer_log.txt", 'w')
data_file = open("data.txt", "w")
cap = 6200
maintenance_lim = 3000
maintenance = 180
system_clock = 0
old_system_clock = 0
baseline_uptime = 0
total_system_uptime = 0
total_system_transfers = 0
time_stepper = 30
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
        cur.execute(
            "UPDATE unit_state SET assets = " + str(len(assets_in_unit(unit))) + ", state = 1 WHERE unit_id = '" + unit + "'")
        cur.execute("SELECT asset_demand FROM unit" + unit + " WHERE id = 1")
        cur.execute(
            "UPDATE unit_state SET assets_required = " + str(cur.fetchall()[0][0]) + " WHERE unit_id = '" + unit + "'")

    # cur.execute("SELECT * FROM unit_state")
    # print(cur.fetchall())

def initialize_asset_states():
    cur.execute("SELECT id,curr_util_value FROM asset_states")
    assets = cur.fetchall()
    for asset in assets:
        maintenance_count = int(asset[1] / maintenance_lim)
        cur.execute("UPDATE asset_states SET maintenance_count = " + str(maintenance_count) + "WHERE id = " + str(asset[0]))
    cur.execute("SELECT * FROM asset_states")
    #print(cur.fetchall())

# ----------------------------------------DETECTING NEXT EVENT-------------------------------------------

def set_events():
    cur.execute("SELECT * FROM unit_state WHERE unit_id = 'A'")
    print(cur.fetchone())
    cur.execute("TRUNCATE TABLE events")
    for unit_id in unit_ids:
        find_unit_event(unit_id)


def find_unit_event(unit_id):
    cur.execute("SELECT state,assets, assets_required FROM unit_state WHERE unit_id = '" + unit_id + "'")
    line = cur.fetchone()
    state = line[0]
    assets_in = len(assets_in_unit(unit_id))

    unit_table = 'unit' + unit_id

    cur.execute("SELECT COUNT(id) FROM " + unit_table)
    schedule_length = cur.fetchone()[0]
    if state != -1:
        cur.execute(
            "SELECT start_date, end_date, asset_demand, util_type, rate_unit, rate_value FROM " + unit_table +
            " LEFT OUTER JOIN phases ON " + unit_table + ".phase = phases.phase_id WHERE " + unit_table + ".id = " + str(
                state))

        phase = cur.fetchone()
        cur.execute("SELECT * FROM asset_states WHERE curr_unit = '" + unit_id + "'")
        assets = cur.fetchall()
        if assets_in != 0:
            for asset in assets:
                find_asset_event(asset, phase, assets_in)

        cur.execute("SELECT * FROM unit" + unit_id + " WHERE id > " + str(state))

        next_phase = cur.fetchone()
        # print(next_phase)
        # print(unit)

        if next_phase is not None:
            cur.execute("INSERT INTO events(id, object_type, event_date, event_type, new_required)"
                        "VALUES ('" + unit_id + "', 'unit'," + str(next_phase[2]) + ",'PC', " + str(next_phase[4]) + ")")
        else:
            cur.execute("INSERT INTO events(id, object_type, event_date, event_type, new_required)"
                        "VALUES ('" + unit_id + "', 'unit'," + str(phase[1] + 1) + ",'PC', -1)")


def find_asset_event(asset, phase, assets_in):
    if system_clock == 2415:
        jackpot = None
    if asset[0] == 76:
        jackpoot = None
    curr_util = 0
    if asset[4] == 'O':
        curr_util = asset[3]
    if asset[4] == 'M':
        curr_util = asset[5]
    maintenance_checkpoint = (asset[6]+1) * maintenance_lim
    maintenance_checkpoint2 = 180
    end_date = phase[1]
    day_diff = end_date - system_clock+1
    if phase[4] == 'perAsset_PerDay':
        hrs_per_day = int(phase[5])
    else:
        hrs_per_day = phase[5] / assets_in
    added_hours = day_diff * hrs_per_day
    temp_curr_util = curr_util + added_hours
    # if asset[0] == 24:
    #     print(phase)
    #     print(assets_in)
    #     print(added_hours)
    #     print(temp_curr_util)
    # If asset is not in maintenance
    if asset[4] == 'O':
        # Check if asset hits EOL
        if temp_curr_util >= cap:
            remaining = int((cap - curr_util) / hrs_per_day)
            # print(remaining)
            exec_date = system_clock + remaining
            command = "INSERT INTO events (id, object_type, event_date, event_type)  VALUES(" + str(
                asset[0]) + ", 'asset'," + str(exec_date) + ", 'EOL')"
            cur.execute(command)
            # print("Asset " + str(asset[0]) + " EOL ")

        # Check if asset hits maintenance
        if temp_curr_util >= maintenance_checkpoint:

            remaining = int((maintenance_checkpoint - curr_util) / hrs_per_day)
            # print(remaining)
            exec_date = system_clock + remaining
            # print("Asset " + asset_id + " in maintenance on "+ str(exec_date))
            command = """
                            INSERT INTO events (id, object_type, event_date, event_type)
                            VALUES(""" + str(asset[0]) + ", 'asset'," + str(exec_date) + ", 'M')"

            cur.execute(command)


    # If asset was in maintenance
    elif asset[4] == 'M':
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
    nearest_events = []
    cur.execute("SELECT * FROM events")
    events = cur.fetchall()
    if len(events) == 0:
        end_condition = True
        return
   # print(events)
    nearest = events[0]
    for event in events:
        if event[2] == nearest[2]:
            nearest_events.append(event)
        if event[2] < nearest[2]:
            nearest_events.clear()
            nearest_events.append(event)
            nearest = event
    print("------------------------------------ next events: ")
    for event in nearest_events:
        print(event)

    system_clock = nearest[2]
    update_assets()

    for event in nearest_events:
        logger.write("\nAt " + str(datetime.strftime(clock_zero + timedelta(days=event[2]), date_format)) + ": " + str(
            event[1]) + " " + str(event[0]) + " " + str(event[3]) + "\n")
        # print("next event is: " + str(nearest))
        # print(system_clock)
        execute_event(event)


def execute_event(event):
        event_id = event[0]
        # Update asset state
        # Update unit_state.assets
        if event[1] == 'asset':

            cur.execute("SELECT * FROM asset_states WHERE id = '" + event_id + "'")
            asset = cur.fetchone()
            if event[3] == "M":
                cur.execute("UPDATE asset_states SET state = 'M' WHERE id = " + str(event_id))
                cur.execute("SELECT curr_unit FROM asset_states WHERE id = " + str(event_id))
                curr_unit = cur.fetchone()[0]
                print("current unit: " + str(curr_unit))
                cur.execute("UPDATE unit_state SET assets = unit_state.assets-1 WHERE unit_id = '" + curr_unit + "'")
                cur.execute("SELECT assets FROM unit_state WHERE unit_id = '" + curr_unit + "'")
                tep = cur.fetchone()
                if tep[0] < 0:
                    print("maintenance put unit " + curr_unit + " in the negatives: " + str(tep))

            elif event[3] == 'EOL':
                cur.execute("UPDATE asset_states SET state = 'EOL', maintenance =0 WHERE id = " + str(event_id))
                cur.execute("SELECT curr_unit FROM asset_states WHERE id = " + str(event_id))
                curr_unit = cur.fetchone()[0]
                cur.execute(
                    "UPDATE unit_state SET assets = unit_state.assets-1 WHERE unit_id = '" + curr_unit + "'")
                cur.execute("SELECT assets FROM unit_state WHERE unit_id = '" + curr_unit + "'")
                tep = cur.fetchone()
                if tep[0] < 0:
                    print("eol put unit " + curr_unit + " in the negatives: " + str(tep))

            elif event[3] == "EM":
                cur.execute("UPDATE asset_states SET state = 'O', maintenance_count = maintenance_count+1, maintenance = 0 WHERE id = " + event_id)
                cur.execute("SELECT curr_unit FROM asset_states WHERE id = " + str(event_id))
                curr_unit = cur.fetchone()[0]
                cur.execute("UPDATE unit_state SET assets = unit_state.assets+1 WHERE unit_id = '" + curr_unit + "'")


        # Update unit state
        # Update unit_state.asset_requirement
        # Update next event in events table
        elif event[1] == 'unit':
            if event[4] == -1:
                cur.execute("UPDATE unit_state SET state = -1, assets_required = 0, schedule_end = " + str(system_clock) + " WHERE unit_id = '" + event_id + "'")
            else:
                cur.execute("UPDATE unit_state SET state = unit_state.state+1, assets_required = " + str(
                    event[4]) + " WHERE unit_id = '" + event_id + "'")

# -------------------------------------------UPDATING STATE-----------------------------------------------
def update_assets():
    day_diff = system_clock - old_system_clock
    for unit in unit_ids:
        cur.execute("SELECT state, assets, assets_required FROM unit_state WHERE unit_id = '" + unit + "'")
        line = cur.fetchone()
        if line[0] !=-1:
            assets = len(assets_in_unit(unit))
            if assets != 0:
                state = line[0]
                table = 'unit' + unit
                cur.execute(
                    "SELECT phase, asset_demand, rate_unit, rate_value FROM unit" + unit + " RIGHT OUTER JOIN phases ON phases.phase_id = " + table + ".phase WHERE " + table + ".id = " + str(
                        state))
                phase = cur.fetchone()
                if phase[2] == 'perAsset_PerDay':
                    hrs_per_day = int(phase[3])
                else:
                    hrs_per_day = phase[3] / assets
                added_hours = day_diff * hrs_per_day
                #if added_hours == 0:
                    #print(added_hours)
                    #end_condition = True

                cur.execute("UPDATE asset_states SET curr_util_value = curr_util_value + " + str(
                    added_hours) + " WHERE curr_unit = '" + unit + "' AND state = 'O'")
                cur.execute("UPDATE asset_states SET maintenance = maintenance + " + str(
                    added_hours) + " WHERE curr_unit = '" + unit + "' AND state = 'M'")
    cur.execute("SELECT * FROM asset_states WHERE state = 'O'")
    test = cur.fetchall()
    for t in test:
        hours = t[3]
        if hours > cap:
            print("asset " + str(t[0]) + " has exceeded cap: " + str(hours))
            global end_condition
            # end_condition = True



def transfer(asset, unit_a, unit_b):
    global total_system_transfers
    asset_id = str(asset[0])
    cur.execute("UPDATE asset_states SET curr_unit = '" + unit_b + "' WHERE id = " + asset_id)
    cur.execute("UPDATE unit_state SET assets = unit_state.assets-1, transfers = transfers-1 WHERE unit_id = '" + unit_a + "'")
    cur.execute("UPDATE unit_state SET assets = unit_state.assets+1, transfers = transfers +1 WHERE unit_id = '" + unit_b + "'")
    cur.execute("SELECT assets FROM unit_state WHERE unit_id = '" + unit_a + "'")
    tep = cur.fetchone()
    if tep[0] <0:
        print("transfer put unit " + unit_a + " in the negatives")
    total_system_transfers += 1



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
    evaluation_max = 500
    while not options_exhausted and len(empty_spots) > 0 and options_evaluated < evaluation_max:
        #options_evaluated += 1
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
        option_depth = 2
        spot_indices = increment_index(spot_indices, spot_options, option_depth, 0)
        # print(option_ids)
        # USE FOR RANDOM SELECTION
        # spot_indices = get_rand_option(spot_options)

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
    curr_phase_status = cur.fetchall()[0][0]
    if curr_phase_status == -1:
        return 30
    else:
        cur.execute("SELECT phase FROM unit" + unit_id + " WHERE id = " + str(curr_phase_status))
        phase = cur.fetchall()[0][0]
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
            score_uptime += phase_weight * new_state * alpha * unit_downtime[unit_id]
        else:
            score_uptime += phase_weight * alpha * unit_downtime[unit_id]

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
        if unit[1] != -1:
            if unit[4] != 0:
                period_downtime = int((system_clock - old_system_clock) * max(0, ((unit[4] - unit[3]) / float(unit[4]))))
            else:
                period_downtime = 0
            cur.execute("UPDATE unit_state SET downtime = unit_state.downtime +" + str(
                period_downtime) + " WHERE unit_id = '" + unit[0] + "'")
            total_system_uptime = total_system_uptime - period_downtime


def get_holes():
    cur.execute("SELECT * FROM unit_state WHERE assets < assets_required AND state > 0")
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

def initialize_data_files():
    global data_file_dict
    data_file_dict['global'] = open('data.txt','w')
    for unit in unit_ids:
        data_file_dict[unit] = open('data_' + unit + '.txt', 'w')


def record_event_data():
    # finding the states
    cur.execute("SELECT COUNT(state) FROM asset_states WHERE state = 'O'")
    data_file_dict['global'].write(str(cur.fetchone()[0]) + "|")
    cur.execute("SELECT COUNT(state) FROM asset_states WHERE state = 'M'")
    data_file_dict['global'].write(str(cur.fetchone()[0]) + "|")
    cur.execute("SELECT COUNT(state) FROM asset_states WHERE state = 'EOL'")
    data_file_dict['global'].write(str(cur.fetchone()[0]) + "|")
    cur.execute("SELECT SUM(assets_required) FROM unit_state")
    data_file_dict['global'].write(str(cur.fetchone()[0]) + "|")
    data_file_dict['global'].write(str(system_clock)+ '\n')

    for key,value in data_file_dict.items():
        if key != 'global':
            cur.execute("SELECT schedule_end FROM unit_state WHERE unit_id = '" + key + "'")
            if cur.fetchone()[0] is None:
                cur.execute("SELECT COUNT(state) FROM asset_states WHERE curr_unit = '" + key + "' AND state = 'O'" )
                value.write(str(cur.fetchone()[0]) + '|')
                cur.execute("SELECT COUNT(state) FROM asset_states WHERE curr_unit = '" + key + "' AND state = 'M'" )
                value.write(str(cur.fetchone()[0]) + '|')
                cur.execute("SELECT COUNT(state) FROM asset_states WHERE curr_unit = '" + key + "' AND state = 'EOL'" )
                value.write(str(cur.fetchone()[0]) + '|')
                cur.execute("SELECT assets_required, transfers FROM unit_state WHERE unit_id = '" + key + "'")
                temp = cur.fetchone()
                value.write(str(temp[0]) + '|')
                value.write(str(temp[1]) + '|')
                value.write(str(system_clock) + '\n')
            # global end_condition
            # end_condition = True

def close_data_files():
    for key,value in data_file_dict.items():
        value.write("end")
        value.close()


if __name__ == '__main__':

    initialize_unit_states()
    initialize_asset_states()
    initialize_data_files()

    # count = 0
    while end_condition is False:
        # if count > 20:
        #     break
        cur.execute("UPDATE unit_state SET transfers = 0")
        calculate_downtime()
        old_system_clock = system_clock
        calculate_average_uptime()
        set_events()
        find_next_event()
        # cur.execute("SELECT * FROM unit_state WHERE unit_id = 'J'")
        # print(cur.fetchone())
        if end_condition is True:
            break
        boom = generate_options(get_holes())
        if boom[0] is not None:
            for b in boom[0]:
                transfer(b[0], b[1], b[2])
                logger.write("    Asset " + str(b[0][0]) + " was transferred from " + b[1] + " to " + b[2] + ", action score = " + str(boom[1]) + "\n")

        else:
            logger.write("    No action was taken, action score = " + str(boom[1]) + "\n")
        day_diff = system_clock - old_system_clock
        if day_diff < 0:
            print("day diff is negative. check for bugs")
            break
        logger.write("\n-----------------\n")
        record_event_data()
        # count = count +1
    print("Exiting Simulation")
    logger.write("\nTotal Transfers: " + str(total_system_transfers))

    cur.execute("select * from unit_state")
    unit_states = cur.fetchall()

    avg_uptime = 0


    for unit in unit_states:
        u_id = unit[0]
        if unit[7] is None:
            uptime = 100 - 100 * (float(unit[2]) / float(system_clock))
        else:
            uptime = 100 - 100 * (float(unit[2]) / float(unit[7]))
        logger.write("\nUnit " + str(u_id) + " uptime is " + str(uptime) + "%")
        avg_uptime += uptime

    logger.write("\nAverage System Uptime is " + str(avg_uptime / len(unit_states)) + "%")
    close_data_files()

logger.close()
cur.close()
conn.commit()
