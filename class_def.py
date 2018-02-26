# Unit definition

from copy import copy, deepcopy
from enum import Enum
#from oo_simulation import get_object


class State(Enum):
    ONLINE = 0
    MAINTENANCE = 1
    OFFLINE = 2


class Unit:

    def __init__(self, u_id, first_phase):
        self.id = u_id

        self.__assets = {}
        self.__schedule = []
        self.__eos_time = first_phase[2]

        self.append_phase(first_phase)

        self.__phase_idx = 0
        self.__state = State.ONLINE
        self.__cumulative_downtime = 0

    # appends in order (phase id, start_dt, end_dt, assets_required)
    def append_phase(self, phase):
        self.__schedule.append(phase)
        self.__eos_time = max(self.__eos_time, int(phase[2]))

    def asset_demand(self):
        if self.__state == State.ONLINE:
            return self.__schedule[self.__phase_idx][3]
        else:
            return 0

    def asset_shortage(self):
        return self.asset_demand() - self.online_asset_count()

    def update(self, time_elapsed, phases):
        assets_required = self.__schedule[self.__phase_idx][3]

        performance = float(self.online_asset_count())/float(assets_required)

        self.__cumulative_downtime += (1 - performance)*time_elapsed

        curr_util_rates = phases[self.current_phase()].util_rates

        # updating asset utilizations
        if self.__state == State.ONLINE:
            for asset_id, asset in self.__assets.items():
                if asset.state() == State.ONLINE:
                    for util_type, rate in curr_util_rates.items():

                        if rate[0] == "perUnit_perDay":
                            util_rate = float(rate[1]) / float(self.online_asset_count())
                        else:
                            util_rate = rate[1]
                        asset.update_util(time_elapsed*util_rate, util_type)

    def transfer_asset(self, asset, unit_to, time):
        self.__remove_asset(asset)

        unit_to.add_asset(asset)
        asset.transfer(unit_to, time)

    def get_downtime_pct(self, system_clock):
        return float(self.__cumulative_downtime) / float(system_clock)

    def add_asset(self, asset):
        self.__assets[asset.id] = asset
        self.raise_flags()

    def __remove_asset(self, asset):
        del self.__assets[asset.id]
        self.raise_flags()

    def current_phase(self):
        if self.__state == State.ONLINE:
            return self.__schedule[self.__phase_idx][0]
        else:
            return "EOS"
        
    def get_schedule(self):
        return self.__schedule

    def eos_time(self):
        return self.__eos_time

    def online_asset_count(self):
        count = 0
        for asset_id, asset in self.__assets.items():
            if asset.state() == State.ONLINE:
                count += 1

        return count

    def change_phase(self):
        self.__phase_idx += 1

        for asset_id, asset in self.__assets.items():
            asset.raise_flag()

    def end_schedule(self):
        if self.__phase_idx >= len(self.__schedule):
            self.__state = State.OFFLINE
        self.raise_flags()

    def raise_flags(self):
        for asset_id, asset in self.__assets.items():
            asset.raise_flag()

    def state(self):
        return self.__state


class Asset:
    # initial utilization should be a dict keyed on utilization type name
    def __init__(self, a_id, initial_util, first_unit, type):
        self.id = a_id
        self.__util = initial_util
        self.unit = first_unit
        self.__type = type
        self.__update_flag = False
        self.__future_events = []
        self.__state = State.ONLINE
        self.__time_last_transferred = 0

        # 0 is online, 1 is offline,

    #def __update(self, time):
     #   update = 4
        # need to grab util rates, from units?
        # returns a maintenance / end of life event if relevant maybe
        # maybe separate update and event_check methods

    def update_util(self, hours, util_type):
        self.__util[util_type] += hours

    def get_util(self, util_type):
        return self.__util[util_type]

    def flag_up(self):
        return self.__update_flag

    def raise_flag(self):
        self.__update_flag = True
        self.__future_events = []

    def update(self, new_future_events):
        self.__update_flag = False
        self.__future_events = new_future_events

    def future_events(self):
        return deepcopy(self.__future_events)

    def enter_maintenance(self):
        self.__state = State.MAINTENANCE

    def exit_maintenance(self):
        self.__state = State.ONLINE

    def end_of_life(self):
        self.__state = State.OFFLINE

    def state(self):
        return self.__state

    def transfer(self, unit, time):
        self.__time_last_transferred = time
        self.unit = unit

    def transfer_time(self):
        return self.__time_last_transferred

    def next_event_time(self):
        if len(self.__future_events) > 0:
            earliest_time = self.__future_events[0].time
            for event in self.__future_events:
                earliest_time = max(event.time, earliest_time)

            return earliest_time

        else:
            return -1


# more of a struct really
class Phase:

    def __init__(self, p_id, priority):
        self.id = p_id
        self.priority = int(priority)
        self.util_rates = {}

    def add_util_type(self, util_type, rate_type, rate):
        self.util_rates[util_type] = (rate_type, float(rate))


# also more of a struct really
class Hurdle:

    def __init__(self, id, util_type, util_hurdle, maint_length):
        self.id = id
        self.util_type = util_type
        self.hurdle = util_hurdle
        self.length = maint_length


class Event:

    def __init__(self, time):
        self.time = time


class PhaseChangeEvent(Event):

    def __init__(self, time, unit, phase):
        Event.__init__(self,time)
        self.unit = unit
        self.phase = phase
        self.type = 'PC'


class MaintenanceEvent(Event):

    # state is TRUE if going INTO maintenance, FALSE if coming OUT of maintenance
    def __init__(self, time, asset, offline, hurdle):
        Event.__init__(self, time)
        self.asset = asset
        self.offline = offline
        self.hurdle = hurdle

        # 'MS' = Maintenance Start
        # 'ME' = Maintenance End
        if offline:
            self.type = 'MS'
        else:
            self.type = 'ME'


class EOLEvent(Event):

    def __init__(self, time, asset, util_type):
        Event.__init__(self, time)
        self.asset = asset
        self.util_type = util_type
        self.type = 'EOL'


class EOSEvent(Event):

    def __init__(self, time, unit):
        Event.__init__(self,time)
        self.unit = unit
        self.type = 'EOS'
