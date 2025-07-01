from utils.parser import read_map_file, read_scen_file
from algorithms.pp import PrioritizedPlanningSolver
from visualize import plot_paths  

import os
import time

# Garante que a pasta de resultados exista
os.makedirs("results", exist_ok=True)

def main():
    # Caminhos para os arquivos de exemplo
    map_file = 'examples/random-32-32-20.map'
    scen_file = 'examples/random-32-32-20-random-1.scen'

    # Leitura dos dados
    map_data = read_map_file(map_file)
    starts, goals = read_scen_file(scen_file, num_agents=5)  # teste inicial com 5 agentes

    # Planejamento
    solver = PrioritizedPlanningSolver(map_data, starts, goals)
    start_time = time.time()    
    paths = solver.plan_paths() 
    
    runtime = time.time() - start_time

    total_cost = sum(len(path) - 1 for path in paths)

    # Saída
    if paths is None:
        print("Falha ao encontrar caminhos para todos os agentes.")
    else:
        for i, path in enumerate(paths):
            print(f"Agente {i}: {path}")

        # (Opcional) salvar em arquivo
        with open("results/solution_output.txt", "w") as f:
            for i, path in enumerate(paths):
                f.write(f"Agente {i}: {path}\n")
                
        # Visualização dos caminhos
        plot_paths(map_data, starts, goals, paths)
        
        print(f"\nTempo de execução: {runtime:.4f} segundos")

        print(f"Soma dos comprimentos dos caminhos: {total_cost}")

        # Salvar em arquivo
        with open("results/pp_python_results.txt", "w") as f:
            f.write(f"Tempo de execução: {runtime:.4f} segundos\n")
            f.write(f"Soma dos comprimentos dos caminhos: {total_cost}\n")


if __name__ == "__main__":
    main()
