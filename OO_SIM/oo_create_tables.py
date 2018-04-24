from datetime import datetime, timedelta
from class_def import Unit, Asset, Phase, Hurdle
import csv
import sys

# Important Global Variables
START_DATE = "2018-01-01"
DATE_FORMAT = "%Y-%m-%d"
clock_zero = None


def create_phase_data(filepath):
    # phase dict structure: Phase ID - Key
    # Vals - priority - util rates (dict of UtilType (key) to (RateUnit, RateValue) tuple)
    phases = {}
    with open(filepath+'Phase_Asset_Priority.csv', 'rt', encoding='utf-8') as priority_file:
        reader = csv.reader(priority_file, dialect='excel')
        next(reader)
        for row in reader:
            phases[row[0]] = Phase(row[0], int(row[1]))
        phases["EOS"] = Phase("EOS", 100)
    with open(filepath+'Utilization_Rates.csv', 'rt', encoding='utf-8') as util_rate_file:
        reader = csv.reader(util_rate_file, dialect='excel')
        next(reader)
        for row in reader:
            if phases[row[0]] is not None:
                phases[row[0]].add_util_type(row[1], row[2], float(row[3]))
    phases["EOS"].add_util_type("Hours", "perAsset_perDay", 0)
    phases["EOS"].add_util_type("Cycles", "perAsset_perDay", 0)

    return phases


def create_units(filepath):

    units = {}
    with open(filepath+'Unit_Schedule.csv', 'rt', encoding='utf-8') as unit_schedule_file:
        reader = csv.reader(unit_schedule_file, dialect='excel')
        next(reader)
        for row in reader:
            unit_id = row[0]
            row[2] = int(date_to_int(row[2]))
            row[3] = int(date_to_int(row[3]))
            row[4] = int(row[4])
            if unit_id in units:
                units[unit_id].append_phase(row[1:5])
            else:
                units[unit_id] = Unit(unit_id, row[1:5])

    return units


def create_assets(units,filepath):

    assets = {}
    with open(filepath+'Asset_Initial_Utilization_v2.csv', 'rt', encoding='utf-8') as asset_util_file:
        with open(filepath+'Asset_Schedule.csv', 'rt', encoding='utf-8') as asset_schedule_file:
            reader = csv.reader(asset_util_file, dialect='excel')
            reader2 = csv.reader(asset_schedule_file, dialect='excel')
            next(reader)
            next(reader2)

            for util_row, sched_row in zip(reader, reader2):
                id = util_row[0]
                num_util = int((len(util_row) - 2) / 2)

                initial_util = {}
                for i in range(num_util):
                    util_name = util_row[2+2*i]
                    util_val = float(util_row[3+2*i])

                    initial_util[util_name] = util_val

                # placeholder for more types
                type = 1

                unit = sched_row[1]

                assets[id] = Asset(id, initial_util, units[unit], type)

                units[unit].add_asset(assets[id])
    return assets


def misc_data(filepath):

    with open(filepath+'Utilization_Limits.csv', 'rt', encoding='utf-8') as util_limits_file:
        reader = csv.reader(util_limits_file, dialect='excel')
        next(reader)

        util_limits = {}

        for row in reader:
            util_limits[row[0]] = int(row[1])

    with open(filepath+'Maintenance_Hurdles.csv', 'rt', encoding='utf-8') as main_hurdle_file:
        reader = csv.reader(main_hurdle_file,dialect='excel')
        next(reader)

        maintenance_hurdles = {}

        for row in reader:
            # hurdle ID, utilization type, utilization hurdle, hour length
            maintenance_hurdles[row[0]] = Hurdle(row[0], row[1], int(row[2]), int(row[3]))

    return util_limits, maintenance_hurdles


def date_to_int(date):
    global clock_zero
    temp = datetime.strptime(date, DATE_FORMAT)
    return (temp - clock_zero).days


def main(filepath):
    global clock_zero
    clock_zero = datetime.strptime(START_DATE, DATE_FORMAT)

    phases = create_phase_data(filepath)
    units = create_units(filepath)
    assets = create_assets(units,filepath)

    util_limits, maintenance_hurdles = misc_data(filepath)
    return phases, units, assets, util_limits, maintenance_hurdles


if __name__ == '__main__':
    main(sys.argv[1])
