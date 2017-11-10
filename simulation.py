import psycopg2
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
cur.execute("SELECT * FROM downtime")
unit_ids = []
temp = cur.fetchall()
for unit in temp:
    unit_ids.append(unit[0])
# go through each asset and find the next event
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
            start_time = transfer[1]
            end_time = transfer[2]
            day_diff = end_time-start_time
            # print(str(day_diff))
            cur.execute("""SELECT * FROM phases
             WHERE phase_id = '""" + transfer[0] + "'")
            phase = cur.fetchone()
            # print(phase)
            if phase[2] == 'perAsset_PerDay':
                hrs_per_day = int(phase[3])
            else:
                hrs_per_day = phase[3]/transfer[3]

            added_hours = day_diff * hrs_per_day
            temp_curr_util = curr_util + added_hours
            # record the events appropriately in the event table
            # update the state of the asset in the asset table
            # freeze the data
            if temp_curr_util >=maintenance_checkpoint:

                remaining = int((maintenance_checkpoint - curr_util)/hrs_per_day)
                # print(remaining)
                exec_date = start_time+ remaining
                print("Asset " + asset_id + " in maintenance on "+ str(exec_date))
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
    find_next_event()
    update_state()

def update_state():
    # print(unit_ids)
    for unit in unit_ids:
        cur.execute("SELECT * FROM unit" + unit)
        unit_schedule = cur.fetchall()
        for time in unit_schedule:
            print("system clock: " + str(system_clock))
            if time[3] > system_clock:
                curr_phase = time[0]

                cur.execute("SELECT phase_id FROM ")
    # update asset states
    # pop off unit schedule rows


def find_next_event():
    global system_clock
    cur.execute("SELECT * FROM events")
    events = cur.fetchall()
    nearest = events[0]
    for event in events:
        if event[2]<nearest[2]:
            nearest = event
    system_clock = nearest[2]

def assets_in_unit(unit_id):
    cur.execute("SELECT * FROM asset_states WHERE curr_unit = '" + unit_id + "'")
    print(cur.fetchall())

if __name__ == '__main__':
    asset_milestone()
    update_state()

cur.close()
conn.commit()