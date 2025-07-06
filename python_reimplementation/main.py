from utils.parser import read_map_file, read_scen_file
from algorithms.pp import PrioritizedPlanningSolver, Agent
from visualize import plot_paths
from animate import Animation
import os
import time
import random
import matplotlib.pyplot as plt
import multiprocessing

# Ensure that the results folder exists
os.makedirs("results", exist_ok=True)

AGENT_COUNT = 15  # Default number of agents, can be adjusted
RANDOMIZER = 0.3  # Randomization factor for LNS replanning
TIMEOUT = 30  # Timeout for the LNS replanning in seconds
RANDOMIZE_AGENTS = False  # Whether to randomize agents before initial planning


class MAPFResults:
    def __init__(self, map_data, starts, goals, paths, runtime, total_cost):
        self.map_data = map_data
        self.starts = starts
        self.goals = goals
        self.paths = paths
        self.runtime = runtime
        self.total_cost = total_cost


def planner(queue):
    # Paths to the example files
    map_file = "python_reimplementation/examples/random-32-32-20.map"
    scen_file = "python_reimplementation/examples/random-32-32-20-random-1.scen"
    initial_exhibition_data = None
    final_exhibition_data = None
    global AGENT_COUNT, RANDOMIZER, TIMEOUT

    # Data reading
    map_data = read_map_file(map_file)
    starts, goals = read_scen_file(
        scen_file, num_agents=AGENT_COUNT
    )  # initial test with 5 agents

    idx = 0
    agents = []
    for start, goal in zip(starts, goals):
        agents.append(Agent(idx, start, goal))

    if RANDOMIZE_AGENTS:
        random.shuffle(agents)

    for agent in agents:
        agent.id = idx
        idx += 1

    # Planning
    solver = PrioritizedPlanningSolver(map_data, agents)

    start_time = time.time()
    agents = solver.plan_paths()
    runtime = time.time() - start_time
    paths = [agent.path for agent in agents] if agents else None
    total_cost = sum(len(path) - 1 for path in paths)

    # Replan paths using LNS
    execution_number = 0
    best_cost = total_cost
    print(f"Initial total cost: {total_cost} in execution {execution_number}")
    initial_exhibition_data = MAPFResults(
        map_data=map_data,
        starts=starts,
        goals=goals,
        paths=paths,
        runtime=runtime,
        total_cost=total_cost,
    )

    print("Starting LNS replanning...")
    while True:
        agents_copy = agents.copy()
        execution_number += 1
        random_agents = random.sample(
            agents_copy, k=min(round(AGENT_COUNT * RANDOMIZER), len(agents_copy))
        )

        # print("Replanning paths for the following agents:")
        for agent in agents_copy:
            if agent in random_agents:
                # print(f"Agent {agent.id} from {agent.start} to {agent.goal}")
                agent.path = []

        # Move empty agents to the end of the list
        agents_copy = move_empty_agents_to_end(agents_copy)

        new_solver = PrioritizedPlanningSolver(map_data, agents_copy)

        new_solver.plan_paths()
        runtime = time.time() - start_time
        agents_copy = reorder_agents_by_id(agents_copy)  # Reorder agents by ID
        paths = [agent.path for agent in agents_copy] if agents_copy else None

        total_cost = sum(len(path) - 1 for path in paths)

        if total_cost < best_cost:
            best_cost = total_cost
            agents = agents_copy  # Update the agents with the new paths
            final_exhibition_data = MAPFResults(
                map_data=map_data,
                starts=starts,
                goals=goals,
                paths=paths,
                runtime=runtime,
                total_cost=total_cost,
            )
            print(f"\tNew best cost found: {best_cost} in execution {execution_number}")
        try:
            queue.get(block=False)
            # If the queue is not empty, it means the main process has requested to stop
            break
        except multiprocessing.queues.Empty:
            # If the queue is empty, continue with the next iteration
            pass

    queue.put(
        {
            "Initial Solution": initial_exhibition_data,
            "Final Solution": final_exhibition_data,
        }
    )  # Send the final exhibition data to the main process


def move_empty_agents_to_end(agents):
    """
    Move agents with empty paths to the end of the list.
    """
    empty_agents = [agent for agent in agents if not agent.path]
    non_empty_agents = [agent for agent in agents if agent.path]
    return non_empty_agents + empty_agents


def reorder_agents_by_id(agents):
    """
    Reorder agents by their IDs.
    """
    return sorted(agents, key=lambda agent: agent.id)


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
    p = multiprocessing.Process(target=planner, name="MAPF_Planner", args=(queue,))
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
