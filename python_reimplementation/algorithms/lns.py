# algorithms/lns.py

import heapq
import random
from collections import defaultdict
from visualize import detect_collisions

class LNSPlanner:
    def __init__(self, map_data, starts, goals, num_iterations=10):
        self.map_data = map_data
        self.starts = starts
        self.goals = goals
        self.num_iterations = num_iterations
        self.num_agents = len(starts)
        self.paths = []
        self.cost_evolution = []

    def plan(self):
        # Planejamento inicial com todos os agentes
        solver = PrioritizedPlanningSolver(self.map_data, self.starts, self.goals)
        self.paths = solver.plan_paths()
        self.cost_evolution = [sum(len(p) - 1 for p in self.paths)] if self.paths else []

        if self.paths is None:
            return None, self.cost_evolution

        for iteration in range(self.num_iterations):
            print(f"\n🔁 Iteração {iteration + 1}/{self.num_iterations}")

            collisions = detect_collisions(self.paths, return_agents=True)
            if not collisions:
                print("✅ Nenhuma colisão detectada.")
                break

            agents_to_replan = list(set(collisions))

            sub_starts = [self.starts[i] for i in agents_to_replan]
            sub_goals = [self.goals[i] for i in agents_to_replan]

            solver = PrioritizedPlanningSolver(self.map_data, sub_starts, sub_goals)
            sub_paths = solver.plan_paths()

            if sub_paths:
                for idx, agent_idx in enumerate(agents_to_replan):
                    self.paths[agent_idx] = sub_paths[idx]
                self.cost_evolution.append(sum(len(p) - 1 for p in self.paths))
            else:
                print(" Replanejamento falhou para os agentes:", agents_to_replan)

        return self.paths, self.cost_evolution


class PrioritizedPlanningSolver:
    def __init__(self, map_data, starts, goals):
        self.map = map_data
        self.starts = starts
        self.goals = goals

    def plan_paths(self):
        paths = []
        for i, (start, goal) in enumerate(zip(self.starts, self.goals)):
            constraint_table = self.build_constraint_table(paths)
            path = self.a_star(start, goal, constraint_table)
            if path is None:
                print(f"Agente {i} falhou em encontrar um caminho.")
                return None
            paths.append(path)
        return paths

    def build_constraint_table(self, paths):
        table = defaultdict(set)
        for path in paths:
            for t, pos in enumerate(path):
                table[t].add(pos)
            for t in range(len(path), len(path) + 10):
                table[t].add(path[-1])
        return table

    def a_star(self, start, goal, constraint_table):
        open_list = []
        heapq.heappush(open_list, (manhattan_distance(start, goal), 0, start, [start]))
        closed_set = set()

        rows, cols = len(self.map), len(self.map[0])
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

                if 0 <= nx < rows and 0 <= ny < cols and self.map[nx][ny] == '.':
                    neighbor = (nx, ny)
                    if neighbor in constraint_table.get(g + 1, set()):
                        continue
                    new_path = path + [neighbor]
                    heapq.heappush(open_list, (
                        g + 1 + manhattan_distance(neighbor, goal),
                        g + 1,
                        neighbor,
                        new_path
                    ))

        return None

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
