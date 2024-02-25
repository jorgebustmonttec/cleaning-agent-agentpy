import agentpy as ap
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from random import randint

DIRECCIONES = [ #direcciones en las que se puede mover el robot
    (0, 1), (1, 1), (1, 0), (1, -1),
    (0, -1), (-1, -1), (-1, 0), (-1, 1),
]

class CleaningModel(ap.Model):
    def setup(self):
        # se crean los robots
        num_robots = int(self.p['robots'])
        robots = self.agents = ap.AgentList(self, num_robots)

        # se crean los agentes de basura
        num_trash = int(self.p['trash_density'] * self.p['width'] * self.p['height'])
        self.num_trash = num_trash
        trash = ap.AgentList(self, num_trash)
        self.agents.extend(trash)

        # se crea el grid
        self.ground = ap.Grid(self, (self.p['width'], self.p['height']), track_empty=True, check_border=True)
        self.ground.add_agents(robots, [(1, 1)] * num_robots, empty=False)
        self.ground.add_agents(trash, random=True, empty=True)

        # identificar los agentes
        robots.type = 'r'
        trash.type = 't'
        #las celdas limpias seran 'c'

        #variables para estadisticas
        self.steps = 0
        self.moves = 0
        self.is_stopped = False  # para detener la simulación
 
    def step(self):
        #se detiene si ya no hay basura o si se llega al limite de pasos
        ground_trash = self.agents.select(self.agents.type == 't')
        if len(ground_trash) == 0 or self.steps >= self.p['steps']:
            self.end()
            self.stop()
            self.is_stopped = True # para detener la simulación


        for robot in self.agents.select(self.agents.type == 'r'):
            robot_x, robot_y = self.ground.positions[robot]
            hay_basura = False

            for agente in self.ground.agents[robot_x, robot_y]:
                # si hay basura, limpiarla
                if agente.type == 't':
                    agente.type = 'c'
                    hay_basura = True
                    break
            if not hay_basura:
                # si no, moverse a una celda adyacente
                or_robot_x, or_robot_y = robot_x, robot_y
                self.ground.move_by(robot, DIRECCIONES[randint(0, 7)])
                if (or_robot_x, or_robot_y) != self.ground.positions[robot]:
                    # si se movio, aumentar el contador de movimientos
                    self.moves += 1
        # aumentar el contador de pasos
        self.steps += 1

    def end(self):
        #calculo e impresion de estadisticas
        print(f'La simulacion ha terminado en {self.steps} pasos y {self.moves} movimientos')
        porcentaje = (self.num_trash - len(self.agents.select(self.agents.type == 't'))) / self.num_trash
        print(f'Porcentaje de basura limpiada: {porcentaje * 100}%')


# Parametros de la simulación
parametros = {'robots': 3, 
              'trash_density': 0.1, 
              'width': 15, 
              'height': 15, 
              'steps': 100}

def graficar(modelo):
    fig, ax = plt.subplots()
    ax.set_xlim(0, modelo.p['width'])
    ax.set_ylim(0, modelo.p['height'])

    def init():
        return []

    def animate(i):
        if modelo.is_stopped:  
            return []  # Detener la animación si la simulación ha terminado
        ax.clear()
        ax.set_xlim(0, modelo.p['width'])
        ax.set_ylim(0, modelo.p['height'])
        
        # Calcular basura restante y porcentaje de limpieza
        basura_restante = len(modelo.agents.select(modelo.agents.type == 't'))
        porcentaje_limpiado = (modelo.num_trash - basura_restante) / modelo.num_trash * 100
        
        # Actualizar el gráfico con los agentes
        for agente in modelo.agents:
            if agente.type == 'r':
                ax.plot(modelo.ground.positions[agente][0], modelo.ground.positions[agente][1], 'bo')
            elif agente.type == 't':
                ax.plot(modelo.ground.positions[agente][0], modelo.ground.positions[agente][1], 'ro')
            else:
                ax.plot(modelo.ground.positions[agente][0], modelo.ground.positions[agente][1], 'go')
        
        # Mostrar información de la simulación
        info_texto = f'Pasos: {modelo.steps}, Movimientos: {modelo.moves}, Basura Restante: {basura_restante}, Porcentaje Limpiado: {porcentaje_limpiado:.2f}%'
        ax.set_title(info_texto)
        
        modelo.step()
        return []

    ani = FuncAnimation(fig, animate, frames=100, init_func=init, blit=True)
    plt.show()

# Crear y ejecutar la simulación
modelo = CleaningModel(parametros)
modelo.setup()
graficar(modelo)
