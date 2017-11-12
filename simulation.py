import psycopg2
from datetime import datetime, timedelta
date_format = "%Y-%m-%d"

try:
    conn = psycopg2.connect("dbname='test' user='postgres' host='localhost' password='pass'")
except:
    print ("I am unable to connect to the database")

cur = conn.cursor()

cap = 12000
maintenance_lim = 8000
maintenance = 180
system_clock = 0
old_system_clock = 0
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
            if temp_curr_util >=maintenance_checkpoint:

                remaining = int((maintenance_checkpoint - curr_util)/hrs_per_day)
                # print(remaining)
                exec_date = start_time+ remaining
                # print("Asset " + asset_id + " in maintenance on "+ str(exec_date))
                command = """
                                INSERT INTO "events" (id, object_type, event_date, event_type)
                                VALUES('""" + asset_id + "', 'asset',"+ str(exec_date) + ", 'maintenance')"

                cur.execute(command)
                break

            elif curr_util >= cap:
                print("asset " + asset_id + "EOL")
                command = """
                        INSERT INTO "events" (id, object_type, event_date, event_type)
                        VALUES('""" + str(asset[0]) + """', 'asset', 'placeholder', 'EOL')
                        """
                cur.execute(command)
                print("Asset " + asset_id + " EOL ")

                break
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

if __name__ == '__main__':
    initialize_unit_states()
    asset_milestone()
    update_state()

cur.close()
conn.commit()
