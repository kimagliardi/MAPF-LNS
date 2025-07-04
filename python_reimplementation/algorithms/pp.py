import heapq


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class PrioritizedPlanningSolver:
    def __init__(self, map_data, starts, goals):
        self.map = map_data
        self.starts = starts
        self.goals = goals

    def plan_paths(self):
        all_paths = []
        constraints = []
        for start, goal in zip(self.starts, self.goals):
            # Validate start and goal positions
            if start == goal:
                continue
            if self.map[start[0]][start[1]] != "." or self.map[goal[0]][goal[1]] != ".":
                raise ValueError(f"Invalid start or goal position: {start}, {goal}")

            # Find path using A* algorithm
            path = self.a_star(start, goal, constraints)

            if path is None:
                raise ValueError(f"No path found from {start} to {goal}")
            all_paths.append(path)

            # Update constraints with the new path
            for time, position in enumerate(path):
                if time <= len(path) - 1:
                    constraints.append(
                        {
                            "position": position,
                            "time": time,
                            "agent": len(all_paths) - 1,
                            "is_goal": position == goal,
                        }
                    )
        return all_paths

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
                    if self.map[nx][ny] == ".":  # free cell
                        neighbor = (nx, ny)
                        if (neighbor, g + 1) not in closed_set:
                            new_path = path + [neighbor]
                            new_cost = g + 1
                            heapq.heappush(
                                open_list,
                                (
                                    new_cost + manhattan_distance(neighbor, goal),
                                    new_cost,
                                    neighbor,
                                    new_path,
                                ),
                            )

        return None  # no path found
