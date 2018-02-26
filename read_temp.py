def read_unit_data(unit):
    online_assets = []
    maintenance_assets = []
    eol_assets = []
    assets_required = []
    transfers = []
    time_steps = []
    reader = open("data_" + unit + ".txt", 'r')
    for line in reader.readlines():
        if line == 'end':
            break
        data_array = line.split('|')
        online_assets.append(int(data_array[0]))
        maintenance_assets.append(int(data_array[1]))
        eol_assets.append(int(data_array[2]))
        assets_required.append(int(data_array[3]))
        transfers.append(int(data_array[4]))
        time_steps.append(int(data_array[5]))

    return (online_assets,maintenance_assets,eol_assets,assets_required,transfers,time_steps)


def read_global_data():
    online_assets = []
    maintenance_assets = []
    eol_assets = []
    assets_required = []
    time_steps = []

    reader = open("data.txt", 'r')

    for line in reader.readlines():
        if line == 'end':
            break
        data_array = line.split('|')
        online_assets.append(int(data_array[0]))
        maintenance_assets.append(int(data_array[1]))
        eol_assets.append(int(data_array[2]))
        assets_required.append(int(data_array[3]))
        time_steps.append(int(data_array[4]))

    return (online_assets,maintenance_assets,eol_assets,assets_required,time_steps)


print(read_unit_data('A'))
print("-------------------------------------")
print(read_global_data())