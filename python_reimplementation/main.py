from utils.parser import read_map_file, read_scen_file
from algorithms.pp import PrioritizedPlanningSolver
from visualize import plot_paths  
from animate import Animation
import os
import time

# Ensure that the results folder exists
os.makedirs("results", exist_ok=True)

def main():
    # Paths to the example files
    map_file = 'examples/random-32-32-20.map'
    scen_file = 'examples/random-32-32-20-random-1.scen'

    # Data reading
    map_data = read_map_file(map_file)
    starts, goals = read_scen_file(scen_file, num_agents=5)  # initial test with 5 agents

    # Planning
    solver = PrioritizedPlanningSolver(map_data, starts, goals)

    start_time = time.time()
    paths = solver.plan_paths()     
    runtime = time.time() - start_time

    total_cost = sum(len(path) - 1 for path in paths)

    # Output
    if paths is None:
        print("Failed to find paths for all agents.")
    else:
        for i, path in enumerate(paths):
            print(f"Agent {i}: {path}")

        # (Optional) save to file
        with open("results/solution_output.txt", "w") as f:
            for i, path in enumerate(paths):
                f.write(f"Agent {i}: {path}\n")
                
        # Visualization of the paths
        plot_paths(map_data, starts, goals, paths)
        
        print("Paths visualized and saved to results/paths_visualization.png")
        # Animation of the paths
        animation = Animation(map_data, starts, goals, paths)
        animation.show()

        print(f"\nExecution time: {runtime:.4f} seconds")

        print(f"Sum of path lengths: {total_cost}")

        # Save to file
        with open("results/pp_python_results.txt", "w") as f:
            f.write(f"Execution time: {runtime:.4f} seconds\n")
            f.write(f"Sum of path lengths: {total_cost}\n")


if __name__ == "__main__":
    main()
