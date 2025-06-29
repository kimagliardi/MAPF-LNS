import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def plot_paths(map_data, starts, goals, paths, output_file="results/paths_visualization.png"):
    rows = len(map_data)
    cols = len(map_data[0])
    fig, ax = plt.subplots(figsize=(cols / 2, rows / 2))

    # Desenha o mapa
    for x in range(rows):
        for y in range(cols):
            if map_data[x][y] != '.':
                ax.add_patch(patches.Rectangle((y, rows - x - 1), 1, 1, color='black'))

    # Desenha os caminhos dos agentes
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i, path in enumerate(paths):
        color = colors[i % len(colors)]
        for j in range(len(path) - 1):
            x1, y1 = path[j]
            x2, y2 = path[j + 1]
            ax.plot([y1 + 0.5, y2 + 0.5], [rows - x1 - 0.5, rows - x2 - 0.5], color=color, linewidth=2)

        # Marca início e fim
        sx, sy = path[0]
        gx, gy = path[-1]
        ax.add_patch(patches.Circle((sy + 0.5, rows - sx - 0.5), 0.3, color=color, alpha=0.7))
        ax.add_patch(patches.Rectangle((gy + 0.2, rows - gx - 0.8), 0.6, 0.6, edgecolor=color, facecolor='none', lw=2))

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()

    os.makedirs("results", exist_ok=True)
    plt.savefig(output_file)
    plt.close()
