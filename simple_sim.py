# phases will be enum values
# those values will be a variable in a unit object
#
import unicodecsv



class Phase:
    def __init__(self, name, ru, rv):
        self.name = name
        self.rate_unit = ru
        self.rate_value = rv


class Unit:
    phase = Phase(0,0,0)
    def __init__(self, init_phase):
        self.phase = init_phase

    def setPhase(self, newPhase):
        self.phase = newPhase

    def print(self):
        print("unit phase is " + str(Unit.phase.rate_value))

class Asset:

    def __init__(self, init_val, init_unit):
        self.iv = init_val
        self.iu = init_unit
    def transfer(self, to):
        self.iu = to




def import_phases():
    phases = []
    f = open("Utilization_Rates.csv", 'rb')
    reader = unicodecsv.reader(f, encoding='utf-8')
    next(f)
    for row in reader:
        print(row)
        if row[2] == "perUnit_perDay":
            phases.append(Phase(row[0], 0, row[3]))
        else:
            phases.append(Phase(row[0], 1, row[3]))
    return phases

def import_units():
    units = []
    f = open(Unit)
imported_phases = import_phases();
for p in imported_phases:
    print("Phase: " + p.name + " Unit: " + str(p.rate_unit) + " Value: "+ str(p.rate_value))




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