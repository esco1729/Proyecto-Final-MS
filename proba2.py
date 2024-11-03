import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors
from matplotlib.widgets import Slider, Button

GRID_SIZE = (50, 50)
EMPTY = 0
PREY = 1
PREDATOR = 2

colors_list = ['white', 'lightgreen', 'yellowgreen', 'darkgreen', 'red']
cmap = colors.ListedColormap(colors_list)
np.random.seed(42)

#Parámetros iniciales
prey_birth_rate = 0.02 #tasa inicial de nacimientos de presas
predator_birth_rate = 0.02 #tasa inicial de nacimientos de depredadores
predator_death_rate = 0.05 #tasa inicial de muerte de depredadores
speed_factor = 1.0 #factor de velocidad
is_running = True
generation_count = 0

def initialize_grid():
    grid = np.zeros(GRID_SIZE, dtype=int)
    # Se colocan las presas y depredadores aleatoriamente
    for i in range(GRID_SIZE[0]):
        for j in range(GRID_SIZE[1]):
            rand = np.random.rand()
            if rand < 0.15:
                grid[i, j] = PREY
            elif rand < 0.20:
                grid[i, j] = PREDATOR
            else:
                grid[i, j] = EMPTY
    return grid

grid = initialize_grid()
fear_grid = np.zeros(GRID_SIZE, dtype=int)

# Total de poblaciones
prey_counts = []
predator_counts = []

def update_grid(grid, fear_grid):
    new_grid = np.copy(grid)
    new_fear_grid = np.copy(fear_grid)

    for i in range(GRID_SIZE[0]):
        for j in range(GRID_SIZE[1]):
            if grid[i, j] == PREY:
                # Verificar si los depredadores en la vecindad para ajustar el miedo
                neighbors = [
                    ((i-1)%GRID_SIZE[0], j),
                    ((i+1)%GRID_SIZE[0], j),
                    (i, (j-1)%GRID_SIZE[1]),
                    (i, (j+1)%GRID_SIZE[1])
                ]
                fear = 0
                for ni, nj in neighbors:
                    if grid[ni, nj] == PREDATOR:
                        fear += 1
                if fear >= 2:
                    new_fear_grid[i, j] = 2  # Nivel alto de miedo
                elif fear == 1:
                    new_fear_grid[i, j] = 1  # Nivel medio de miedo
                else:
                    new_fear_grid[i, j] = 0  # Nivel bajo de miedo

                # Movimiento de presas basándose en miedo
                move_options = []
                for ni, nj in neighbors:
                    if new_grid[ni, nj] == EMPTY:
                        move_options.append((ni, nj))
                if move_options:
                    # Las tasas más altas de miedo hace que las presas se muevan más rápido
                    if new_fear_grid[i, j] == 2:
                        chosen_move = move_options[np.random.randint(len(move_options))]
                        new_grid[chosen_move] = PREY
                        new_fear_grid[chosen_move] = new_fear_grid[i, j]
                        new_grid[i, j] = EMPTY
                        new_fear_grid[i, j] = 0
                    elif new_fear_grid[i, j] == 1 and np.random.rand() < 0.5:
                        chosen_move = move_options[np.random.randint(len(move_options))]
                        new_grid[chosen_move] = PREY
                        new_fear_grid[chosen_move] = new_fear_grid[i, j]
                        new_grid[i, j] = EMPTY
                        new_fear_grid[i, j] = 0
                    # Las presas con el miedo ma´s bajo no se mueven

                # Reproducción
                if np.random.rand() < prey_birth_rate:
                    empty_neighbors = [(ni, nj) for ni, nj in neighbors if new_grid[ni, nj] == EMPTY]
                    if empty_neighbors:
                        reproduce_cell = empty_neighbors[np.random.randint(len(empty_neighbors))]
                        new_grid[reproduce_cell] = PREY
                        new_fear_grid[reproduce_cell] = 0

            elif grid[i, j] == PREDATOR:
                # Movimiento aleatorio de depredadores
                move_options = []
                neighbors = [
                    ((i-1)%GRID_SIZE[0], j),
                    ((i+1)%GRID_SIZE[0], j),
                    (i, (j-1)%GRID_SIZE[1]),
                    (i, (j+1)%GRID_SIZE[1])
                ]
                for ni, nj in neighbors:
                    if new_grid[ni, nj] in [EMPTY, PREY]:
                        move_options.append((ni, nj))
                if move_options:
                    chosen_move = move_options[np.random.randint(len(move_options))]
                    # Ver si alguna presa se mueve
                    if new_grid[chosen_move] == PREY:
                        # El depredador se come a la presa
                        new_grid[chosen_move] = PREDATOR
                        new_grid[i, j] = EMPTY
                        new_fear_grid[chosen_move] = 0
                    else:
                        # Celda vacía
                        new_grid[chosen_move] = PREDATOR
                        new_grid[i, j] = EMPTY

                # Reproducción depredador
                if np.random.rand() < predator_birth_rate:
                    empty_neighbors = [(ni, nj) for ni, nj in neighbors if new_grid[ni, nj] == EMPTY]
                    if empty_neighbors:
                        reproduce_cell = empty_neighbors[np.random.randint(len(empty_neighbors))]
                        new_grid[reproduce_cell] = PREDATOR

                # Hambre de depredador
                if np.random.rand() < predator_death_rate:
                    new_grid[i, j] = EMPTY

    return new_grid, new_fear_grid

def visualize_simulation(grid, fear_grid):
    global ani, is_running, generation_count, prey_counts, predator_counts

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))
    plt.subplots_adjust(left=0.1, bottom=0.3)

    # Inicializar visualización
    visualization_grid = np.zeros_like(grid, dtype=int)
    for i in range(GRID_SIZE[0]):
        for j in range(GRID_SIZE[1]):
            if grid[i, j] == PREY:
                visualization_grid[i, j] = 1 + fear_grid[i, j]  # 1, 2, o 3 basado en nivel de miedo (velocidad de movimiento)
            elif grid[i, j] == PREDATOR:
                visualization_grid[i, j] = 4  # Depredador
            else:
                visualization_grid[i, j] = 0  # Vacío

    mat = ax1.matshow(visualization_grid, cmap=cmap)
    ax1.set_title("Presa-depredador")
    ax1.axis('off')

    prey_line, = ax2.plot([], [], label='Presas')
    predator_line, = ax2.plot([], [], label='Depredadores')
    ax2.set_xlim(0, 200)
    ax2.set_ylim(0, GRID_SIZE[0]*GRID_SIZE[1] // 2)
    ax2.set_xlabel('Tiempo')
    ax2.set_ylabel('Población')
    ax2.set_title('Población respecto al tiempo')
    ax2.legend()

    gen_text = fig.text(0.05, 0.95, 'Generación: 0')
    prey_count_text = fig.text(0.05, 0.92, 'Total presas: 0')
    predator_count_text = fig.text(0.05, 0.89, 'Total depredadores: 0')


    axcolor = 'lightgoldenrodyellow'
    ax_prey_birth_rate = plt.axes([0.3, 0.2, 0.5, 0.03], facecolor=axcolor)
    prey_birth_slider = Slider(ax_prey_birth_rate, 'Nacimientos de presas', 0.0, 0.1, valinit=prey_birth_rate)

    ax_predator_birth_rate = plt.axes([0.3, 0.15, 0.5, 0.03], facecolor=axcolor)
    predator_birth_slider = Slider(ax_predator_birth_rate, 'Nacimientos de depredadores', 0.0, 0.1, valinit=predator_birth_rate)

    ax_predator_death_rate = plt.axes([0.3, 0.1, 0.5, 0.03], facecolor=axcolor)
    predator_death_slider = Slider(ax_predator_death_rate, 'Muertes de depresadores', 0.0, 0.1, valinit=predator_death_rate)

    ax_sim_speed = plt.axes([0.3, 0.05, 0.5, 0.03], facecolor=axcolor)
    sim_speed_slider = Slider(ax_sim_speed, 'Velocidad de simulación', 0.1, 5.0, valinit=speed_factor)

    # Botones
    ax_start = plt.axes([0.7, 0.01, 0.1, 0.04])
    button_start = Button(ax_start, 'Start')

    ax_stop = plt.axes([0.81, 0.01, 0.1, 0.04])
    button_stop = Button(ax_stop, 'Stop')

    ax_reset = plt.axes([0.59, 0.01, 0.1, 0.04])
    button_reset = Button(ax_reset, 'Reset')

    # Funciones de los sliders
    def update_prey_birth_rate(val):
        global prey_birth_rate
        prey_birth_rate = val

    prey_birth_slider.on_changed(update_prey_birth_rate)

    def update_predator_birth_rate(val):
        global predator_birth_rate
        predator_birth_rate = val

    predator_birth_slider.on_changed(update_predator_birth_rate)

    def update_predator_death_rate(val):
        global predator_death_rate
        predator_death_rate = val

    predator_death_slider.on_changed(update_predator_death_rate)

    def update_simulation_speed(val):
        global ani
        speed_factor = val
        new_interval = 200 / speed_factor
        ani.event_source.interval = new_interval

    sim_speed_slider.on_changed(update_simulation_speed)

    def start_simulation(event):
        global is_running
        is_running = True

    button_start.on_clicked(start_simulation)

    def stop_simulation(event):
        global is_running
        is_running = False

    button_stop.on_clicked(stop_simulation)

    def reset_simulation(event):
        global grid, fear_grid, prey_counts, predator_counts, is_running, generation_count
        is_running = False
        grid[:] = initialize_grid()
        fear_grid[:] = np.zeros(GRID_SIZE, dtype=int)
        prey_counts.clear()
        predator_counts.clear()
        generation_count = 0
        is_running = True

    button_reset.on_clicked(reset_simulation)

    # Actualizar animación
    def update_frame(frame):
        global grid, fear_grid, prey_counts, predator_counts, is_running, generation_count

        if not is_running:
            return [mat, prey_line, predator_line]

        grid, fear_grid = update_grid(grid, fear_grid)

        # Actualizar grid de visualización
        visualization_grid = np.zeros_like(grid, dtype=int)
        for i in range(GRID_SIZE[0]):
            for j in range(GRID_SIZE[1]):
                if grid[i, j] == PREY:
                    visualization_grid[i, j] = 1 + fear_grid[i, j]  # 1, 2, or 3
                elif grid[i, j] == PREDATOR:
                    visualization_grid[i, j] = 4
                else:
                    visualization_grid[i, j] = 0

        mat.set_data(visualization_grid)

        # Actualizar poblaciones
        prey_count = np.count_nonzero(grid == PREY)
        predator_count = np.count_nonzero(grid == PREDATOR)
        prey_counts.append(prey_count)
        predator_counts.append(predator_count)

        prey_line.set_data(range(len(prey_counts)), prey_counts)
        predator_line.set_data(range(len(predator_counts)), predator_counts)
        ax2.set_xlim(0, max(200, len(prey_counts)))
        ax2.set_ylim(0, max(max(prey_counts + [0]), max(predator_counts + [0])) + 10)

        # Actualización de textos
        generation_count += 1
        gen_text.set_text('Generación: {}'.format(generation_count))
        prey_count_text.set_text('Total de presas: {}'.format(prey_count))
        predator_count_text.set_text('Total de depredadores: {}'.format(predator_count))

        return [mat, prey_line, predator_line]

    ani = animation.FuncAnimation(fig, update_frame, frames=200, interval=200, blit=False)
    plt.show()

visualize_simulation(grid, fear_grid)
