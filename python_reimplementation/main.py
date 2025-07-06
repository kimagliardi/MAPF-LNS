from mapf_lns import planner
from visualize import plot_paths
from animate import Animation
import os
import time
import matplotlib.pyplot as plt
import multiprocessing

# Ensure that the results folder exists
os.makedirs("results", exist_ok=True)

AGENT_COUNT = 15  # Default number of agents, can be adjusted
RANDOMIZER = 0.3  # Randomization factor for LNS replanning
TIMEOUT = 30  # Timeout for the LNS replanning in seconds
RANDOMIZE_AGENTS = False  # Whether to randomize agents before initial planning


def save_paths_to_file(paths, filename):
    with open(filename, "w") as f:
        for i, path in enumerate(paths):
            f.write(f"Agent {i}: {path}\n")


def store_results_to_file(initial_exhibition_data, final_exhibition_data):

    print("Exhibition completed.")
    print(
        f"Initial solution execution time: {initial_exhibition_data.runtime:.4f} seconds"
    )
    print(f"Initial total cost: {initial_exhibition_data.total_cost}")
    print(f"Final solution execution time: {final_exhibition_data.runtime:.4f} seconds")
    print(f"Final total cost: {final_exhibition_data.total_cost}")

    # Save to file
    with open("results/pp_python_initial_results.txt", "w") as f:
        f.write(f"Execution time: {initial_exhibition_data.runtime:.4f} seconds\n")
        f.write(f"Sum of path lengths: {initial_exhibition_data.total_cost}\n")
    with open("results/pp_python_final_results.txt", "w") as f:
        f.write(f"Execution time: {final_exhibition_data.runtime:.4f} seconds\n")
        f.write(f"Sum of path lengths: {final_exhibition_data.total_cost}\n")

    save_paths_to_file(initial_exhibition_data.paths, "results/paths.txt")
    save_paths_to_file(final_exhibition_data.paths, "results/optimized_paths.txt")


def animate_results(exhibition_data, chart_title="MAPF Paths Visualization"):

    # Visualization of the paths
    plot_paths(
        exhibition_data.map_data,
        exhibition_data.starts,
        exhibition_data.goals,
        exhibition_data.paths,
    )
    # Animation of the paths
    animation = Animation(
        exhibition_data.map_data,
        exhibition_data.starts,
        exhibition_data.goals,
        exhibition_data.paths,
    )
    animation.fig.canvas.manager.set_window_title(chart_title)
    animation.show()
    plt.show()


def main():

    queue = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=planner,
        name="MAPF_Planner",
        args=(
            queue,
            "python_reimplementation/examples/random-32-32-20.map",
            "python_reimplementation/examples/random-32-32-20-random-1.scen",
            AGENT_COUNT,
            RANDOMIZER,
            RANDOMIZE_AGENTS,
        ),
    )
    p.start()

    time.sleep(TIMEOUT)
    queue.put(None)  # Send a signal to stop the planner if it takes too long

    p.join()  # Wait for the planner process to finish
    p.terminate()  # Ensure the planner process is terminated

    solutions = queue.get()
    initial_exhibition_data = solutions["Initial Solution"]
    final_exhibition_data = solutions["Final Solution"]

    e1 = multiprocessing.Process(
        target=animate_results,
        args=(
            initial_exhibition_data,
            "Initial Solution",
        ),
    )
    e2 = multiprocessing.Process(
        target=animate_results,
        args=(
            final_exhibition_data,
            "Final Solution",
        ),
    )

    store_results_to_file(initial_exhibition_data, final_exhibition_data)

    e1.start()
    e2.start()
    e1.join()
    e2.join()

    # Clean up the processes
    if e1.is_alive():
        e1.terminate()
    if e2.is_alive():
        e2.terminate()


if __name__ == "__main__":
    main()
