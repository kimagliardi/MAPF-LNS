import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def animate_paths(map_data, starts, goals, paths, output_file="results/animation_lns.gif"):
    rows, cols = len(map_data), len(map_data[0])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-1, cols)
    ax.set_ylim(-1, rows)
    ax.set_title("Movimentação dos Agentes (LNS + PP)")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    # Obstáculos
    for i in range(rows):
        for j in range(cols):
            if map_data[i][j] != '.':
                ax.add_patch(plt.Rectangle((j, rows - i - 1), 1, 1, color='black'))

    agent_dots = []
    colors = plt.cm.get_cmap("tab10", len(paths))
    for i in range(len(paths)):
        dot, = ax.plot([], [], 'o', color=colors(i), label=f'Agente {i}')
        agent_dots.append(dot)

    max_len = max(len(p) for p in paths)

    def update(frame):
        for i, path in enumerate(paths):
            pos = path[min(frame, len(path)-1)]
            agent_dots[i].set_data([pos[1]], [rows - pos[0] - 1])  # corrigido: usar listas
        return agent_dots


    ani = animation.FuncAnimation(fig, update, frames=max_len, interval=500, blit=True)

    # Salvar animação
    ani.save(output_file, writer='pillow')  # .gif
    print(f" Animação salva em: {output_file}")

    plt.close()
    
def detect_collisions(paths, return_agents=False):
    collisions = []
    max_time = max(len(p) for p in paths)
    occupied = {}

    for t in range(max_time):
        pos_at_t = {}
        for i, path in enumerate(paths):
            pos = path[min(t, len(path) - 1)]
            if pos in pos_at_t:
                j = pos_at_t[pos]
                collisions.append((i, j) if not return_agents else i)
            else:
                pos_at_t[pos] = i

            # Verifica troca de posição (swap)
            if t > 0:
                prev = path[t - 1] if t - 1 < len(path) else path[-1]
                for j, other_path in enumerate(paths):
                    if j != i and t < len(other_path):
                        if prev == other_path[t] and pos == other_path[t - 1]:
                            collisions.append((i, j) if not return_agents else i)

    if return_agents:
        return list(set(collisions))
    return collisions

def plot_paths(map_data, starts, goals, paths, output_file=None):
    fig, ax = plt.subplots()
    rows = len(map_data)
    cols = len(map_data[0])

    # desenha mapa
    for i in range(rows):
        for j in range(cols):
            if map_data[i][j] != '.':
                ax.add_patch(plt.Rectangle((j, rows - i - 1), 1, 1, color='black'))

    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    for i, path in enumerate(paths):
        color = colors[i % len(colors)]
        x = [p[1] + 0.5 for p in path]
        y = [rows - p[0] - 0.5 for p in path]
        ax.plot(x, y, color=color, marker='o', label=f"Agente {i}")

    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend()
    
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

    plt.close()
    
def plot_lns_cost_evolution(cost_evolution, output_file=None):
    """
    Gera o gráfico da evolução do custo ao longo das iterações do LNS.
    """
    plt.figure(figsize=(8, 4))
    plt.plot(cost_evolution, marker='o', linestyle='-', color='blue')
    plt.title("Evolução do Custo - LNS")
    plt.xlabel("Iteração")
    plt.ylabel("Custo Total")
    plt.grid(True)
    
    if output_file:
        plt.savefig(output_file)
        print(f"📈 Gráfico de evolução do custo salvo em: {output_file}")
    else:
        plt.show()

    plt.close()