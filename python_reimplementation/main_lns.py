from utils.parser import read_map_file, read_scen_file
from algorithms.lns import LNSPlanner
from visualize import plot_paths, plot_lns_cost_evolution
from visualize import animate_paths  
from visualize import plot_paths, animate_paths, detect_collisions
from visualize import plot_lns_cost_evolution  


import os
import time

def detect_collisions(paths, output_file=None):
    max_time = max(len(p) for p in paths)
    collision_logs = []
    for t in range(max_time):
        pos_at_t = {}
        for i, path in enumerate(paths):
            pos = path[min(t, len(path) - 1)]  # posição no tempo t
            if pos in pos_at_t:
                msg = f"Colisão detectada no tempo {t} entre agentes {i} e {pos_at_t[pos]} na posição {pos}"
                print(msg)
                collision_logs.append(msg)
            else:
                pos_at_t[pos] = i

            # verificação de troca de posição
            if t > 0:
                prev = path[t - 1] if t - 1 < len(path) else path[-1]
                for j, other_path in enumerate(paths):
                    if j != i and t < len(other_path):
                        if prev == other_path[t] and pos == other_path[t - 1]:
                            msg = f"Colisão de troca no tempo {t} entre agentes {i} e {j}"
                            print(msg)
                            collision_logs.append(msg)

    if output_file and collision_logs:
        with open(output_file, "w") as f:
            for line in collision_logs:
                f.write(line + "\n")
        print(f"\n Relatório de colisões salvo em: {output_file}")
    elif output_file:
        with open(output_file, "w") as f:
            f.write("Nenhuma colisão detectada.\n")
        print(f"\nNenhuma colisão detectada. Relatório salvo em: {output_file}")

def main():
    map_file = 'examples/random-32-32-20.map'
    scen_file = 'examples/random-32-32-20-random-1.scen'

    os.makedirs("results", exist_ok=True)

    map_data = read_map_file(map_file)
    starts, goals = read_scen_file(scen_file, num_agents=10)

    print("🚀 Executando LNS com PP...")
    start_time = time.time()
    lns_solver = LNSPlanner(map_data, starts, goals, num_iterations=20)
    paths, cost_evolution = lns_solver.plan()
    runtime = time.time() - start_time

    if paths is None:
        print("Falha ao encontrar caminhos viáveis.")
    else:
        for i, path in enumerate(paths):
            print(f"Agente {i}: {path}")

        total_cost = sum(len(path) - 1 for path in paths)
        print(f"\nCusto total da solução: {total_cost}")
        print(f"Tempo total de execução: {runtime:.4f} segundos")

        with open("results/solution_output_lns.txt", "w") as f:
            for i, path in enumerate(paths):
                f.write(f"Agente {i}: {path}\n")

        plot_paths(map_data, starts, goals, paths, output_file="results/paths_visualization_lns.png")
        plot_lns_cost_evolution(cost_evolution, output_file="results/lns_cost_evolution.png")

        print("\nVerificando colisões entre agentes...")
        detect_collisions(paths, output_file="results/collision_report.txt")
        
    # Visualizações
    plot_paths(map_data, starts, goals, paths, output_file="results/paths_visualization_lns.png")
    plot_lns_cost_evolution(cost_evolution, output_file="results/lns_cost_evolution.png")
    animate_paths(map_data, starts, goals, paths, output_file="results/animation_lns.gif")



if __name__ == "__main__":
    main()
