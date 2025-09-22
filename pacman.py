"""Pacman, classic arcade game — versión modificada para la evidencia.

Cambios solicitados:
1) Cambiar el tablero (tiles): se rediseñó el laberinto interno conservando bordes.
2) Cambiar forma y color del alimento: de punto blanco a cuadrado dorado.
3) Hacer que los fantasmas vayan más rápido: se redujo el intervalo del temporizador.

Notas:
- 0 = muro (no se dibuja camino).
- 1 = camino con pellet (dibuja pellet) → al comer pasa a 2.
- 2 = camino ya comido (sin pellet).
"""

from random import choice
import turtle as t
from freegames import floor, vector

# ---------------------------- Constantes -------------------------------------
CELL = 20              # tamaño de celda (px)
SPEED = 5              # velocidad base (px por tick) — mantiene alineación con la grilla
TIMER_MS = 70          # << más rápido que 100 ms (original) para subir dificultad

WALL_COLOR = 'blue'    # color de paredes/camino
PELLET_COLOR = 'gold'  # color de pellet (antes era punto blanco)
PELLET_SIZE = 6        # tamaño del pellet cuadrado (px)

# ------------------------------ Estado ---------------------------------------
state = {'score': 0}

# Turtles de dibujo/score (sin forma visible)
path = t.Turtle(visible=False)
writer = t.Turtle(visible=False)

# Dirección actual de Pac-Man (comienza hacia la derecha)
aim = vector(SPEED, 0)

# Posición inicial de Pac-Man (puedes ajustarla si lo piden)
pacman = vector(-40, -80)

# Lista de fantasmas: [posición, dirección]
ghosts = [
    [vector(-180, 160), vector(SPEED, 0)],
    [vector(-180, -160), vector(0, SPEED)],
    [vector(100, 160), vector(0, -SPEED)],
    [vector(100, -160), vector(-SPEED, 0)],
]

# ---------------------------- Tablero (20x20) --------------------------------
# 0 = muro, 1 = camino con pellet, 2 = camino ya comido
# Se rediseñó abriendo/cerrando pasillos para un layout diferente y jugable.
# fmt: off
tiles = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,  # <- abrí un corredor en col 9
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,  # <- uní col 10-11
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,  # <- abrí corredor en col 9
    0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,  # <- conecté bloque central
    0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0,
    0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]
# fmt: on


# --------------------------- Utilidades de dibujo -----------------------------
def square(x: int, y: int) -> None:
    """Dibuja un cuadrado CELL×CELL usando 'path' en (x, y)."""
    path.up()
    path.goto(x, y)
    path.down()
    path.begin_fill()
    for _ in range(4):
        path.forward(CELL)
        path.left(90)
    path.end_fill()


def pellet_square(x: int, y: int) -> None:
    """Dibuja un pellet cuadrado (color y tamaño custom) centrado en la celda."""
    # Centramos el pellet dentro de la celda
    half = PELLET_SIZE // 2
    cx = x + CELL // 2
    cy = y + CELL // 2

    path.up()
    path.goto(cx - half, cy - half)
    path.down()
    path.color(PELLET_COLOR)
    path.begin_fill()
    for _ in range(4):
        path.forward(PELLET_SIZE)
        path.left(90)
    path.end_fill()
    path.color(WALL_COLOR)  # restaurar color para paredes


def offset(point: vector) -> int:
    """Devuelve el índice lineal en 'tiles' para la posición dada."""
    x = (floor(point.x, CELL) + 200) / CELL
    y = (180 - floor(point.y, CELL)) / CELL
    index = int(x + y * 20)
    return index


def valid(point: vector) -> bool:
    """True si 'point' está dentro de caminos (no muro) y alineado a la grilla."""
    index = offset(point)
    if tiles[index] == 0:
        return False

    # Verificación del borde opuesto de la celda (20-1 px)
    index = offset(point + (CELL - 1))
    if tiles[index] == 0:
        return False

    # Mantener movimiento restringido a líneas de la grilla
    return point.x % CELL == 0 or point.y % CELL == 0


def world() -> None:
    """Dibuja el mundo: paredes y pellets."""
    t.bgcolor('black')
    path.color(WALL_COLOR)

    for index, tile in enumerate(tiles):
        if tile > 0:
            x = (index % 20) * CELL - 200
            y = 180 - (index // 20) * CELL
            square(x, y)

            # Dibujar pellet con nueva forma/color cuando tile == 1
            if tile == 1:
                pellet_square(x, y)


def move() -> None:
    """Mueve a Pac-Man y a todos los fantasmas, actualiza score y pantalla."""
    writer.undo()
    writer.write(state['score'])

    t.clear()

    # Mover Pac-Man si la siguiente celda es válida
    if valid(pacman + aim):
        pacman.move(aim)

    # Comer pellet (tile pasa 1 -> 2) y sumar score
    index = offset(pacman)
    if tiles[index] == 1:
        tiles[index] = 2
        state['score'] += 1
        x = (index % 20) * CELL - 200
        y = 180 - (index // 20) * CELL
        square(x, y)  # repinta el camino sin pellet

    # Dibujar Pac-Man
    t.up()
    t.goto(pacman.x + CELL // 2, pacman.y + CELL // 2)
    t.dot(CELL, 'yellow')

    # Mover y dibujar fantasmas
    for point, course in ghosts:
        if valid(point + course):
            point.move(course)
        else:
            options = [vector(SPEED, 0), vector(-SPEED, 0),
                       vector(0, SPEED), vector(0, -SPEED)]
            plan = choice(options)
            course.x = plan.x
            course.y = plan.y

        t.up()
        t.goto(point.x + CELL // 2, point.y + CELL // 2)
        t.dot(CELL, 'red')

    t.update()

    # Colisión simple
    for point, _ in ghosts:
        if abs(pacman - point) < CELL:
            return  # fin de juego

    # << Fantasmas más rápidos: menor intervalo >>
    t.ontimer(move, TIMER_MS)


def change(x: int, y: int) -> None:
    """Cambia la dirección de Pac-Man si el siguiente paso es válido."""
    if valid(pacman + vector(x, y)):
        aim.x = x
        aim.y = y


# ------------------------------ Setup Turtle ---------------------------------
t.setup(420, 420, 370, 0)
t.hideturtle()
t.tracer(False)

writer.goto(160, 160)
writer.color('white')
writer.write(state['score'])

t.listen()
t.onkey(lambda: change(SPEED, 0), 'Right')
t.onkey(lambda: change(-SPEED, 0), 'Left')
t.onkey(lambda: change(0, SPEED), 'Up')
t.onkey(lambda: change(0, -SPEED), 'Down')

world()
move()
t.done()

# sync(board): 2025-09-21T18:43:20-06:00
