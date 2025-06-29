def read_map_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Pula cabeçalho até encontrar a linha 'map'
    map_start_index = 0
    for i, line in enumerate(lines):
        if line.strip().lower() == 'map':
            map_start_index = i + 1
            break

    map_data = []
    for line in lines[map_start_index:]:
        map_data.append(list(line.strip()))

    return map_data


def read_scen_file(filepath, num_agents=5):
    starts, goals = [], []
    with open(filepath, 'r') as f:
        lines = f.readlines()[1:]  # Ignora cabeçalho

    for line in lines[:num_agents]:
        parts = line.strip().split()
        start = (int(parts[5]), int(parts[4]))
        goal = (int(parts[7]), int(parts[6]))
        starts.append(start)
        goals.append(goal)

    return starts, goals