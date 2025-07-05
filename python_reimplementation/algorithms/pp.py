import heapq
from typing import Final
from .a_star import manhattan_distance

UP: Final[tuple] = (-1, 0)
DOWN: Final[tuple] = (1, 0)
LEFT: Final[tuple] = (0, -1)
RIGHT: Final[tuple] = (0, 1)
STILL: Final[tuple] = (0, 0)
DIRECTIONS: Final[list] = [UP, DOWN, LEFT, RIGHT, STILL]  # Up, Down, Left, Right, Still


class Agent:
    def __init__(self, id, start, goal):
        self.id = id
        self.start = start
        self.goal = goal
        self.path = []

    def set_path(self, path):
        self.path = path

    def get_path_length(self):
        return len(self.path) - 1 if self.path else 0

    def is_at_goal(self):
        return self.path and self.path[-1] == self.goal


class PrioritizedPlanningSolver:
    def __init__(self, map_data, starts, goals):
        self.map = map_data
        self.starts = starts
        self.goals = goals
        self.agents = []

        idx = 0
        for start, goal in zip(self.starts, self.goals):
            self.agents.append(Agent(idx, start, goal))
            idx += 1

    def plan_paths(self):
        all_paths = []
        constraints = []
        for agent in self.agents:
            path = self.a_star(agent, constraints)
            agent.set_path(path)
            all_paths.append(agent.path)

            # Update constraints with the new path
            for time, position in enumerate(agent.path):
                for other_agent in self.agents:
                    if other_agent.id != agent.id:
                        # Add constraints for other agents' positions at this time step
                        constraints.append(
                            {
                                "agent": other_agent.id,
                                "position": [position],
                                "time": time,
                                "is_goal": time == len(agent.path) - 1,
                            }
                        )
                        if time < len(agent.path) - 1:
                            constraints.append(
                                {
                                    "agent": agent.id,
                                    "position": [agent.path[time + 1], position],
                                    "time": time + 1,
                                    "is_goal": False,
                                }
                            )

            print(f"Agent {agent.id} path: {agent.path}")
        return all_paths

    def a_star(self, agent, constraints):
        open_list = []
        heapq.heappush(
            open_list,
            (
                manhattan_distance(agent.start, agent.goal),
                0,
                agent.start,
                [agent.start],
            ),
        )
        closed_set = set()
        formatted_constraints = format_constraints(constraints, agent)

        formatted_constraints_by_pos = format_constraints_by_position(
            constraints, agent
        )

        rows = len(self.map)
        cols = len(self.map[0])
        future_constraints = get_when_goal_constrained(
            agent.goal, formatted_constraints_by_pos
        )
        global reached_goal
        reached_goal = False
        while open_list:
            f, g, current, path = heapq.heappop(open_list)

            if current == agent.goal and (
                future_constraints is None or g > max(future_constraints)
            ):
                agent.set_path(path)
                print(f"Found path for agent {agent.id}: {path}")
                return path

            if (current, g) in closed_set:
                continue
            closed_set.add((current, g))

            for direction in DIRECTIONS:
                next_x, next_y = move(current, direction)

                if (0 <= next_x < rows) and (0 <= next_y < cols):
                    if self.map[next_x][next_y] == ".":  # free cell
                        neighbor = (next_x, next_y)
                        if (neighbor, g + 1) not in closed_set:
                            if is_constrained(
                                current, neighbor, g + 1, formatted_constraints
                            ):
                                continue
                            new_path = path + [neighbor]
                            new_cost = g + 1
                            heapq.heappush(
                                open_list,
                                (
                                    new_cost + manhattan_distance(neighbor, agent.goal),
                                    new_cost,
                                    neighbor,
                                    new_path,
                                ),
                            )
                            continue

        return None  # no path found


def format_constraints(constraints, agent):
    """
    Format the constraints for the A* algorithm.
    constraints - list of constraints for the agent
    agent - the agent that is being re-planned
    """
    formatted_constraints = {}
    for c in constraints:
        if c["agent"] == agent.id:
            time = c["time"]
            if time not in formatted_constraints:
                formatted_constraints[time] = [c]
            formatted_constraints[time].append(
                {"position": c["position"], "is_goal": c["is_goal"]}
            )
    return formatted_constraints


def format_constraints_by_position(constraints, agent):
    formatted_constraints = {}
    for c in constraints:
        if c["agent"] == agent.id:
            position = str(c["position"])
            if position not in formatted_constraints:
                formatted_constraints[position] = []
            formatted_constraints[position].append(
                {"time": c["time"], "is_goal": c["is_goal"]}
            )
    return formatted_constraints


def move(loc, direction):
    return [loc[0] + direction[0], loc[1] + direction[1]]


def is_constrained(curr_loc, next_loc, next_time, constraint_table):
    if next_time in constraint_table:
        for constraint in constraint_table[next_time]:
            if [next_loc] == constraint["position"] or [
                curr_loc,
                next_loc,
            ] == constraint["position"]:
                return True
    return False


def get_when_goal_constrained(goal_loc, constraint_table):
    items = constraint_table.get(str([goal_loc]), None)
    if items is None:
        return None
    time_list = [item["time"] for item in items if not item["is_goal"]]
    return time_list
