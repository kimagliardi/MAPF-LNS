import heapq
from collections import defaultdict

class PrioritizedPlanningSolver:    
    def __init__(self, map_data, starts, goals):
        self.map = map_data
        self.starts = starts
        self.goals = goals

    def plan_paths(self):
        paths = []

        for i, (start, goal) in enumerate(zip(self.starts, self.goals)):
            # Gera a constraint_table com base nos caminhos já planejados
            constraint_table = self.build_constraint_table(paths)

            path = self.a_star(start, goal, constraint_table)
            if path is None:
                print(f"Agente {i} falhou em encontrar um caminho.")
                return None
            paths.append(path)

        return paths

    def build_constraint_table(self, paths):
        """
        paths: lista de caminhos já planejados [ [ (x,y), ... ], ... ]
        Retorna um dicionário: t -> set(posições ocupadas por outros agentes)
        """
        table = defaultdict(set)
        for path in paths:
            for t, pos in enumerate(path):
                table[t].add(pos)
            # Após o agente chegar no goal, ele permanece lá (evita colisões no final)
            for t in range(len(path), len(path) + 10):
                table[t].add(path[-1])
        return table

    def a_star(self, start, goal, constraint_table):
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
                    if self.map[nx][ny] == '.':
                        neighbor = (nx, ny)

                        # ⚠️ Verifica se essa posição está ocupada no tempo g+1
                        if neighbor in constraint_table.get(g + 1, set()):
                            continue

                        new_path = path + [neighbor]
                        new_cost = g + 1
                        heapq.heappush(open_list, (
                            new_cost + manhattan_distance(neighbor, goal),
                            new_cost,
                            neighbor,
                            new_path
                        ))

        return None  # Nenhum caminho encontrado

def plan(self):
    # Planejamento inicial com todos os agentes
    solver = PrioritizedPlanningSolver(self.map_data, self.starts, self.goals)
    self.paths = solver.plan_paths()
    cost_evolution = [sum(len(p) - 1 for p in self.paths)] if self.paths else []

    if self.paths is None:
        return None, cost_evolution

    for iteration in range(self.num_iterations):
        print(f"\n🔁 Iteração {iteration + 1}/{self.num_iterations}")

        # 1. Detectar colisões
        collisions = detect_collisions(self.paths, return_agents=True)
        if not collisions:
            print("✅ Nenhuma colisão detectada.")
            break

        # 2. Selecionar agentes para replanejamento
        agents_to_replan = list(set(collisions))

        # 3. Criar novas listas starts e goals
        sub_starts = [self.starts[i] for i in agents_to_replan]
        sub_goals = [self.goals[i] for i in agents_to_replan]

        # 4. Reexecutar PP para o subconjunto
        solver = PrioritizedPlanningSolver(self.map_data, sub_starts, sub_goals)
        sub_paths = solver.plan_paths()

        # 5. Substituir caminhos antigos pelos novos
        if sub_paths:
            for idx, agent_idx in enumerate(agents_to_replan):
                self.paths[agent_idx] = sub_paths[idx]
            cost_evolution.append(sum(len(p) - 1 for p in self.paths))
        else:
            print(" Replanejamento falhou para os agentes:", agents_to_replan)

    return self.paths, cost_evolution

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
