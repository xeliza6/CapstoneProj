# phases will be enum values
# those values will be a variable in a unit object
#
import unicodecsv
from datetime import datetime

phase_dict = {}
unit_dict = {}
MAX_UTIL = 12000

class Phase:
    def __init__(self, ru, rv):
        self.rate_unit = ru
        self.rate_value = rv

#Variables:
# StartDate Array
# EndDate Array
# Phase Array
class Unit:

    def __init__(self, pa, start, end, ad):
        self.phase_array = pa
        self.start_dates = start
        self.end_dates = end
        self.asset_demand = ad

class Asset:

    def __init__(self, id, init_val, init_unit):
        self.iv = init_val
        self.iu = init_unit
        self.id = id
    def transfer(self, to):
        self.iu = to


def import_phases():
    f = open("Utilization_Rates.csv", 'rb')
    reader = unicodecsv.reader(f, encoding='utf-8')
    next(f)
    for row in reader:
        print(row)
        if row[2] == "perUnit_perDay":
            phase = Phase(0, row[3])
        else:
            phase = Phase(1, row[3])
        phase_dict[row[0]] = phase


def import_units():
    f = open("Unit_Schedule.csv", 'rb')
    reader = unicodecsv.reader(f, encoding='utf-8')
    next(f)
    curr_unit = ''
    pa = []
    sd = []
    ed = []
    ad = []
    for row in reader:
        # if unit remains the same this row, update the arrays
        if curr_unit == row[0]:
            pa.append(row[1])
            sd.append(row[2])
            ed.append(row[3])
            ad.append(row[4])
        # if unit changes this row, initialize new unit with arrays and put it in dictionary. Clear and update the new arrays
        else:
            curr_unit = row[0]
            unit = Unit(pa, sd, ed, ad)
            unit_dict[curr_unit] = unit
            curr_unit = row[0]
            pa = []
            sd = []
            ed = []
            ad = []
            pa.append(row[1])
            sd.append(row[2])
            ed.append(row[3])
            ad.append(row[4])

def import_assets():
    asset_array = []
    f1 = open('Asset_Schedule.csv', 'rb')
    f2 = open('Asset_Initial_Utilization.csv', 'rb')
    reader1 = unicodecsv.reader(f1, encoding='utf-8')
    reader2 = unicodecsv.reader(f2, encoding='utf-8')
    next(f1)
    next(f2)
    for row1, row2 in zip(reader1, reader2):
        asset = Asset(row1[0], row2[3],row1[1])
        asset_array.append(asset)
        #print(str(asset.iu) + " and " + str(asset.iv))
    return asset_array



import_phases()
import_units()
assets = import_assets()
date_format = "%Y-%m-%d"

for asset in assets:
    print("Life of asset id: " + asset.id)
    life = float(asset.iv)
    unit = unit_dict[asset.iu]
    for phase, start, end, demand in zip(unit.phase_array, unit.start_dates, unit.end_dates, unit.asset_demand):
        time_left = MAX_UTIL - life
        phase_obj = phase_dict[phase]
        time1 = datetime.strptime(end, date_format)
        time2 = datetime.strptime(start, date_format)
        day_diff = (time1-time2).days
        time_needed = 0
        print("Unit in phase " + phase + " for " + str(day_diff) + " days")
        if phase_obj == 0:
            time_needed = (float(phase_obj.rate_value)/int(demand))*day_diff
        else:
            time_needed = (float(phase_obj.rate_value)) * day_diff
        print("-----Needed: " + str(time_needed) + " \n-----Left: " + str(time_left) )
        if (time_needed >= time_left):
            print("Asset " + asset.id + " has reached max utilization of " + str(MAX_UTIL) + " hours.")
            print("Serving unit: " + asset.iu + ", Phase: " + phase + ", Date: " + start + '\n\n')
            break;
        else:
            life += time_needed



# B = Phase(1,2)
# u = Unit(B)
# u.print()
#
#
# A = Phase(0.1, 10)
# A.print()
#
# u.setPhase(A)
# u.print()