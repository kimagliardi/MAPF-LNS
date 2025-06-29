import heapq
class PrioritizedPlanningSolver:    
    def __init__(self, map_data, starts, goals):
        self.map = map_data
        self.starts = starts
        self.goals = goals

    def plan_paths(self):
        return [[start, goal] for start, goal in zip(self.starts, self.goals)]
    
    def a_star(self, start, goal, constraints):
        open_list = []
        heapq.heappush(open_list, (manhattan_distance(start, goal), 0, start, [start]))
        closed_set = set()

        rows = len(self.map)
        cols = len(self.map[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while open_list:
            f, g, current, path = heapq.heappop(open_list)

            if current == goal:
                return path

            if (current, g) in closed_set:
                continue
            closed_set.add((current, g))

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy

                if 0 <= nx < rows and 0 <= ny < cols:
                    if self.map[nx][ny] == '.':  # célula livre
                        neighbor = (nx, ny)
                        if (neighbor, g + 1) not in closed_set:
                            new_path = path + [neighbor]
                            new_cost = g + 1
                            heapq.heappush(open_list, (
                                new_cost + manhattan_distance(neighbor, goal),
                                new_cost,
                                neighbor,
                                new_path
                            ))

        return None  # nenhum caminho encontrado

