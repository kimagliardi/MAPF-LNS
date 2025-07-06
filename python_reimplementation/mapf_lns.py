from utils.parser import read_map_file, read_scen_file
from algorithms.pp import PrioritizedPlanningSolver, Agent

import random
import time
import multiprocessing


class MAPFResults:
    def __init__(self, map_data, starts, goals, paths, runtime, total_cost):
        self.map_data = map_data
        self.starts = starts
        self.goals = goals
        self.paths = paths
        self.runtime = runtime
        self.total_cost = total_cost


def planner(
    queue,
    map_file=None,
    scen_file=None,
    agent_count=5,
    randomizer=0.3,
    randomize_agents=False,
):
    # Paths to the example files
    map_file = map_file
    scen_file = scen_file
    initial_exhibition_data = None
    final_exhibition_data = None

    # Data reading
    map_data = read_map_file(map_file)
    starts, goals = read_scen_file(
        scen_file, num_agents=agent_count
    )  # initial test with 5 agents

    idx = 0
    agents = []
    for start, goal in zip(starts, goals):
        agents.append(Agent(idx, start, goal))

    if randomize_agents:
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
            agents_copy, k=min(round(agent_count * randomizer), len(agents_copy))
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
