import psycopg2
import csv
from datetime import datetime, timedelta
date_format = "%Y-%m-%d"


try:
    conn = psycopg2.connect("dbname='scheduling' user='postgres' host='localhost' password='simple68'")
except:
    print ("I am unable to connect to the database")

cur = conn.cursor()
clock_zero = datetime.strptime("2018-01-01", date_format)


def create_phases():
    command= """
            CREATE TABLE phases (
                phase_id VARCHAR(2) NOT NULL,
                util_type VARCHAR(255) NOT NULL,
                rate_unit VARCHAR(255) NOT NULL,
                rate_value FLOAT NOT NULL
            )
            """
    cur.execute(command)
    with open('Utilization_Rates.csv', 'rt', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        next(reader)
        for row in reader:
            command = """
            INSERT INTO "phases" (phase_id, util_type, rate_unit, rate_value)
            VALUES ('""" + row[0] + "', '" + row[1] + "','" + row[2] + "','" + row[3] + "')"
            #print(command)
            cur.execute(command)

def drop_phases():
    cur.execute("DROP TABLE IF EXISTS phases")


def create_events():
    command = """
        CREATE TABLE events (
            id  VARCHAR(25) NOT NULL,
            object_type VARCHAR(255) NOT NULL,
            event_date INT NOT NULL,
            event_type VARCHAR(255) NOT NULL
        )
    """
    cur.execute(command)

def drop_events():
    cur.execute("DROP TABLE IF EXISTS events")

def create_units():
    with open('Unit_Schedule.csv', 'rt', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        next(reader)
        for row in reader:
            print("creating table for unit "+ row[0])
            command = """
            CREATE TABLE IF NOT EXISTS unit""" + row[0] + """(
            phase VARCHAR(2) NOT NULL,
            start_date INT NOT NULL,
            end_date INT NOT NULL,
            asset_demand INT NOT NULL)
            """
            print( "command: " + command)
            cur.execute(command)

            cur.execute( """INSERT INTO "unit""" + row[0].lower() + """"(phase,start_date,end_date, asset_demand)
                                VALUES('""" + row[1] + "'," + date_to_int(row[2]) + "," + date_to_int(row[3]) + "," + row[4] + ")")

def drop_units():
    with open('Unit_Schedule.csv', 'rt', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        next(reader)
        for row in reader:
            cur.execute("DROP TABLE IF EXISTS unit" + row[0])

def create_assets():
    command = """
    CREATE TABLE asset_states (
    id INT NOT NULL,
    as_of_date INT NOT NULL,
    util_type VARCHAR(255) NOT NULL,
    curr_unit VARCHAR(2),
    curr_util_value INT NOT NULL,
    num_maintenance INT
    )
    """
    cur.execute(command)
    with open('Asset_Initial_Utilization.csv', 'rt', encoding='utf-8') as csvfile:
        with open('Asset_Schedule.csv', 'rt', encoding='utf-8') as csvfile2:
            reader = csv.reader(csvfile, dialect='excel')
            reader2 = csv.reader(csvfile2, dialect='excel')
            next(reader)
            next(reader2)
            for row, row2 in zip(reader,reader2):
                command = """
                    INSERT INTO "asset_states" (id, as_of_date, util_type, curr_unit, curr_util_value, num_maintenance)
                    VALUES('""" + row[0] + "','" + date_to_int(row[1]) + "','" + row[2] + "','" + row2[1]+"'," + row[3] + ", 0)"
                #print(command)
                cur.execute(command)

def drop_assets():
    cur.execute("DROP TABLE IF EXISTS asset_states")


def create_unit_state():
    command = """
                CREATE TABLE unit_state (
                    unit_id VARCHAR(2) NOT NULL,
                    downtime int NOT NULL,
                    assets int NOT NULL,
                    assets_required int NOT NULL,
                    PRIMARY KEY(unit_id)
                )
                """
    cur.execute(command)
    with open('Unit_Schedule.csv', 'rt', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        next(reader)
        for row in reader:
            command = """
                INSERT INTO "unit_state" (unit_id, downtime, assets, assets_required)
                VALUES ('""" + row[0] +"', 0,0,0)" +"""
                ON CONFLICT DO NOTHING"""
            #print(command)
            cur.execute(command)

def drop_unit_state():
    cur.execute("DROP TABLE IF EXISTS unit_state")

def main():
    #print("main placeholder")
    drop_units()
    create_units()
    drop_assets()
    create_assets()
    drop_phases()
    create_phases()
    drop_events()
    create_events()
    drop_unit_state()
    create_unit_state()

def date_to_int(date):
    temp = datetime.strptime(date, date_format)
    return str((temp - clock_zero).days)

if __name__ == '__main__':
    main()

cur.close()
conn.commit()