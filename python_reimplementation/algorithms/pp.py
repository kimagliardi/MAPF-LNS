import heapq
import random
from typing import Final

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
    def __init__(self, map_data, agents):
        self.map = map_data
        self.agents = agents

    def set_agents(self, agents):
        self.agents = agents

    def plan_paths(self):
        constraints = []
        for agent in self.agents:
            if not agent.path:
                #    print(
                #        f"Planning path for agent {agent.id} from {agent.start} to {agent.goal}"
                #    )
                path = self.a_star(agent, constraints)
                agent.set_path(path)
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
                        constraints.append(
                            {
                                "agent": other_agent.id,
                                "position": [position],
                                "time": time - 1,
                                "is_goal": time == len(agent.path) - 1,
                            }
                        )
                        if time < len(agent.path) - 1:
                            constraints.append(
                                {
                                    "agent": agent.id,
                                    "position": [agent.path[time + 1]],
                                    "time": time + 1,
                                    "is_goal": False,
                                }
                            )

            # print(f"Agent {agent.id} path: {agent.path}")
        return self.agents

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
                # print(f"Found path for agent {agent.id}: {path}")
                return path

            if (current, g) in closed_set:
                continue
            closed_set.add((current, g))

            local_directions = DIRECTIONS.copy()
            random.shuffle(local_directions)
            for direction in local_directions:
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
                formatted_constraints[time] = []
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
            if [next_loc] == constraint["position"]:
                return True
    return False


def get_when_goal_constrained(goal_loc, constraint_table):
    items = constraint_table.get(str([goal_loc]), None)
    if items is None:
        return None
    time_list = [item["time"] for item in items if not item["is_goal"]]
    return time_list


def manhattan_distance(loc1, loc2):
    """
    Calculate the Manhattan distance between two locations.
    loc1 and loc2 are tuples representing (row, column) coordinates.
    """
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
