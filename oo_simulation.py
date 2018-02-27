## Imports and Setups

from class_def import State, Unit, Asset, Phase, Hurdle, Event, PhaseChangeEvent,\
                      MaintenanceEvent, EOLEvent, EOSEvent
import oo_create_tables
from datetime import datetime, timedelta
from math import exp

date_format = "%Y-%m-%d"
clock_zero = datetime.strptime("2018-01-01", date_format)


logger = open("transfer_log.txt", 'w')
data_file = open("data.txt", "w")

## Global Simulation Variables

sim_phases, sim_units, sim_assets, util_limits, maintenance_hurdles = oo_create_tables.main()

# transfers recorded as (asset, unit from, unit to, time)
transfer_record = []
system_state_record = {}

for unit_id in sim_units:
    system_state_record[unit_id] = []

system_state_record['global'] = []

system_clock = 0
old_system_clock = 0


MAINTENANCE_HOURS_PER_DAY = 8


def get_object(obj_type, obj_id):
    obj_type = obj_type.lower()
    if obj_type == "asset":
        return sim_assets[obj_id]
    elif obj_type == "unit":
        return sim_units[obj_id]
    elif obj_type == "phase":
        return sim_phases[obj_id]
    elif obj_type == "hurdle":
        return maintenance_hurdles
    elif obj_type == "limits":
        return util_limits


def generate_starting_events():
    events = []

    # generates all scheduled events
    for unit_id, unit in sim_units.items():
        for unit_phase in unit.get_schedule()[1:]:
            events.append(PhaseChangeEvent(unit_phase[1],unit_id, unit_phase[0]))
        events.append(EOSEvent(unit.eos_time(), unit_id))

    events.sort(key=lambda ev: ev.time)

    return events


def find_unscheduled_events(event):
    global system_clock
    # exploring all assets and units for potential
    # unscheduled events before the current event
    unsched_events = []

    latest_time = event.time
    time_elapsed = latest_time - system_clock

    for id, asset in sim_assets.items():

        # if the events need to be updated
        if asset.flag_up() and asset.state() == State.ONLINE:
            future_asset_events = []

            unit_phase = asset.unit.current_phase()
            curr_util_rates = sim_phases[unit_phase].util_rates

            # finding maintenance entrance events

            for util_type, rate in curr_util_rates.items():
                curr_util = asset.get_util(util_type)

                if rate[0] == "perUnit_perDay":
                    util_rate = rate[1] / float(asset.unit.online_asset_count())
                else:
                    util_rate = rate[1]

                # exploring maintenance hurdles for this utilization type
                for hurdle_id, hurdle in maintenance_hurdles.items():
                    if hurdle.util_type == util_type:
                        if curr_util < hurdle.hurdle and util_rate > 0:
                            time_to_hurdle = (hurdle.hurdle - curr_util) / util_rate
                            new_maintenance = MaintenanceEvent(system_clock + time_to_hurdle, asset.id, True, hurdle)
                            future_asset_events.append(new_maintenance)

                            if time_to_hurdle <= time_elapsed:
                                unsched_events.append(new_maintenance)

                # if there are no remaining maintenance hurdles for this asset
                # the last known event will be end of life, which can now be found
                # it's a waste of time to schedule an end of life event while there
                # are any remaining maintenance hurdles, since it will make it difficult
                # to actually find

                # future asset event list will be empty if end of life is all that remains
                if len(future_asset_events) == 0:
                    time_to_eol = (util_limits[util_type] - curr_util)/ util_rate
                    asset_eol = EOLEvent(system_clock + time_to_eol, asset.id, util_type)
                    future_asset_events.append(asset_eol)

                    if time_to_eol <= time_elapsed:
                        unsched_events.append(asset_eol)

            # updating the asset with the knowledge of future events
            asset.update(future_asset_events)

        else:
            for unsched_event in asset.future_events():
                if unsched_event.time <= event.time:
                    unsched_events.append(unsched_event)

    unsched_events.sort(key=lambda ev: ev.time)
    return unsched_events


def find_next_event(event_list):
    # finds the next event, including interpolating events between phase changes or
    # other predetermined occurrences
    next_planned_event = event_list[0]

    next_events = find_unscheduled_events(next_planned_event)

    if len(next_events) == 0:
        return []
    else:
        event_time = next_events[0].time
        concurrent_events = []
        for event in next_events:
            if event.time == event_time:
                concurrent_events.append(event)
            else:
                break
        if event_time == next_planned_event.time:
            concurrent_events.append(next_planned_event)
        return concurrent_events

# stores system state at each event in dictionary keyed on unit id (keyed on 'global' for
# summary statistics.
# Data stored as (time, online assets, maintenance assets, offline assets, asset demand, asset shortage)
def record_system_state():
    time = system_clock

    # global tracking variables
    global_online_assets = 0
    global_maintenance_assets = 0
    global_offline_assets = 0
    global_asset_demand = 0
    global_shortage = 0

    for unit_id, unit in sim_units.items():
        online = unit.online_asset_count()
        maintenance = unit.maintenance_asset_count()
        offline = unit.offline_asset_count()
        demand = unit.asset_demand()
        shortage = unit.asset_shortage()

        global_online_assets += online
        global_maintenance_assets += maintenance
        global_offline_assets += offline
        global_asset_demand += demand
        global_shortage += shortage

        system_state_record[unit_id].append((time, online, maintenance, offline, demand, shortage))

    system_state_record['global'].append((time, global_online_assets, global_maintenance_assets,
                                         global_offline_assets, global_asset_demand, global_shortage))


def process_event(event, event_list):
    global system_clock
    # processes the event, updates the system, records data, etc.
    for unit_id, unit in sim_units.items():
        unit.update(event.time - system_clock, sim_phases)
    system_clock = event.time

    event_str = "T: " + str(int(event.time)) + " | "

    # handling unique event behavior

    # unit phase change event
    if event.type == 'PC':
        sim_units[event.unit].change_phase()

        event_str += "E: PC | U: " + event.unit + " | "
    # asset maintenance start event
    elif event.type == 'MS':
        sim_assets[event.asset].enter_maintenance()
        sim_assets[event.asset].unit.raise_flags()
        maintenance_length = event.hurdle.length / MAINTENANCE_HOURS_PER_DAY
        # schedule end of maintenance event
        sim_assets[event.asset].update([MaintenanceEvent(system_clock + maintenance_length,event.asset, False, event.hurdle)])
        event_str += "E: MS | A: " + event.asset + " | "
    # asset maintenance exit event
    elif event.type == 'ME':
        sim_assets[event.asset].exit_maintenance()
        sim_assets[event.asset].unit.raise_flags()
        event_str += "E: ME | A: " + event.asset + " | "

    # asset end of life event
    elif event.type == 'EOL':
        sim_assets[event.asset].end_of_life()
        sim_assets[event.asset].unit.raise_flags()
        event_str += "E: EOL | A: " + event.asset + " | "

    # unit end of schedule event
    elif event.type == 'EOS':
        sim_units[event.unit].end_schedule()
        event_str += "E: EOS | U: " + event.unit + " | "

    else:
        print("ERROR: UNRECOGNIZED EVENT TYPE: " + event.type)

    return event_str


def hole_search():

    system_holes = []

    for unit_id, unit in sim_units.items():
        asset_demand = unit.asset_demand()
        asset_shortage = asset_demand - unit.online_asset_count()

        if asset_shortage > 0:
            system_holes.extend([(unit_id, asset_shortage)])

    return system_holes


def temp_unit_states():
    states = {}

    for unit_id, unit in sim_units.items():
        states[unit_id] = (sim_phases[unit.current_phase()].priority, unit.asset_shortage())

    return states


def rank_units(unit_states):

    unit_scores = []
    for unit_id, unit_state in unit_states.items():
        unit = sim_units[unit_id]
        priority = unit_state[0]

        if unit_state[1] > 0:
            unit_scores.append((unit_id, float(priority) / float(unit_state[1])))

    unit_scores.sort(key=lambda unit_data: unit_data[1])

    return unit_scores


def fill_holes(empty_spots):
    total_holes = 0
    for spot in empty_spots:
        total_holes += spot[1]

    # ranking units now
    unit_states = temp_unit_states()
    ranked_units = rank_units(unit_states)
    swapped_assets = []
    transfers = []
    skipped_units = []

    while (len(ranked_units) - len(skipped_units)) > 0:

        for ranked_unit in ranked_units:
            if ranked_unit[0] not in skipped_units:
                targeted_unit_id = ranked_unit[0]
                break
            else:
                targeted_unit_id = None

        unit_to = sim_units[targeted_unit_id]

        best_score = 0.25  # threshold set
        best_option = 0

        for asset_id, asset in sim_assets.items():
            if asset.state() == State.ONLINE and asset_id not in swapped_assets:
                unit_from = asset.unit

                # only examining assets not in the current unit
                if unit_from is not unit_to:
                    unit_from_priority = unit_states[unit_from.id][0]
                    unit_to_priority = unit_states[unit_to.id][0]

                    unit_from_shortage = unit_states[unit_from.id][1]
                    unit_to_shortage = unit_states[unit_to.id][1]

                    # Scoring option
                    if unit_from_priority == 0:
                        score = 0
                    elif unit_to_priority == 0:
                        score = unit_from_priority
                    else:
                        score = (unit_from_priority/unit_to_priority) - \
                            (unit_from_shortage/unit_to_shortage)
                else:
                    score = 0

                if score > best_score:
                    best_score = score
                    best_option = asset_id
                elif score == best_score and best_option != 0:
                    if asset.transfer_time() > sim_assets[best_option].transfer_time():
                        best_score = score
                        best_option = asset_id

        if best_option != 0:
            swapped_assets.append(best_option)
            unit_out_id = sim_assets[best_option].unit.id
            transfers.append((best_option, unit_out_id , targeted_unit_id, best_score))
            # changing temporary unit states

            # adding to shortage
            unit_states[unit_out_id] = (unit_states[unit_out_id][0], unit_states[unit_out_id][1] + 1)
            # subtracting from shortage
            unit_states[targeted_unit_id] = (unit_states[targeted_unit_id][0], unit_states[targeted_unit_id][1] - 1)

            # re-ranking
            ranked_units = rank_units(unit_states)

        # no positive swaps found
        else:
            skipped_units.append(targeted_unit_id)
            ranked_units = rank_units(unit_states)

    # transfer structure is asset_id, unit_from, unit_to
    transfer_str = "Transfers: " + str(len(transfers))

    for transfer in transfers:
        asset = sim_assets[transfer[0]]
        unit_from = sim_units[transfer[1]]
        unit_to = sim_units[transfer[2]]

        unit_from.transfer_asset(asset, unit_to, system_clock)

        # transfers for all time recorded with data format
        # (asset id, unit from id, unit to id, time, and score of the transfer)
        transfer_record.append((asset.id, unit_from.id, unit_to.id, system_clock, transfer[3]))

    return transfer_str


if __name__ == '__main__':
    # main loop goes here

    time_stepper = 30

    event_list = generate_starting_events()

    # main loop
    while len(event_list) > 0:
        next_events = find_next_event(event_list)
        report_str = ""

        # processes events first, handles data updates, etc.
        if len(next_events) == 0:
            # if no intermediate events, pop off the next scheduled event and analyze it
            report_str += process_event(event_list.pop(0), event_list)
            record_system_state()
        else:
            for event in next_events:
                report_str += process_event(event, event_list)
                record_system_state()

        # once events have been processed and changes have been made
        # to the system, search for "holes" and redistribute assets

        # provided there are still events left, conduct transfers
        if len(event_list) > 0:
            holes = hole_search()
            report_str += fill_holes(holes)

        print(report_str)

    print("Num transfers = " + str(len(transfer_record)))
