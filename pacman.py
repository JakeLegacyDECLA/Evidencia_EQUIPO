"""Pacman adaptado a PEP 8 / flake8.

- Líneas <= 180 caracteres
- Separación de funciones con dos líneas
- Imports y constantes ordenadas
- Misma lógica original
"""

import random
import turtle
from turtle import (
    Turtle,
    bgcolor,
    clear,
    hideturtle,
    listen,
    onkey,
    ontimer,
    setup,
    tracer,
    update,
)

# Configuración inicial
WIDTH, HEIGHT = 420, 420
TILE_SIZE = 20
FONT = ("Arial", 16, "normal")  # estilo de fuente consistente

bgcolor("black")
setup(WIDTH, HEIGHT, 370, 0)

# Estados y variables globales
path = Turtle(visible=False)
writer = Turtle(visible=False)
aim = [5, 0]
score = 0

# Posiciones iniciales de los fantasmas
ghosts = [
    [[-180, 160], [5, 0]],
    [[-180, -160], [0, 5]],
    [[100, 160], [0, -5]],
    [[100, -160], [-5, 0]],
]

# Posición inicial de Pacman
pacman = [0, 0]

# Tablero (1 = pared, 0 = vacío, 2 = comida)
tiles = [
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1,
    1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
    1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1,
    1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1,
    1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1,
    1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
]


def square(x, y):
    """Dibuja un cuadrado de lado TILE_SIZE en (x, y)."""
    path.up()
    path.goto(x, y)
    path.down()
    path.begin_fill()
    for _ in range(4):
        path.forward(TILE_SIZE)
        path.left(90)
    path.end_fill()


def offset(point):
    """Convierte coordenadas de punto (x, y) a índice lineal en 'tiles'."""
    x = int((point[0] + 200) // TILE_SIZE)
    y = int((180 - point[1]) // TILE_SIZE)
    return x + y * 20


def valid(point):
    """True si la posición es válida (no choca con pared)."""
    index = offset(point)
    if tiles[index] == 1:
        return False
    return True


def world():
    """Dibuja el tablero del juego."""
    bgcolor("black")
    path.color("blue")
    for index, tile in enumerate(tiles):
        if tile == 1:
            x = (index % 20) * TILE_SIZE - 200
            y = 180 - (index // 20) * TILE_SIZE
            square(x, y)
    update()


def move():
    """Controla el movimiento de Pacman y de los fantasmas."""
    global score

    writer.undo()
    writer.write(score, font=FONT)
    clear()

    if valid([pacman[0] + aim[0], pacman[1] + aim[1]]):
        pacman[0] += aim[0]
        pacman[1] += aim[1]

    index = offset(pacman)
    if tiles[index] == 0:
        tiles[index] = 2
        score += 1
        x = (index % 20) * TILE_SIZE - 200 + 8
        y = 180 - (index // 20) * TILE_SIZE + 8
        path.up()
        path.goto(x, y)
        path.dot(4, "yellow")

    for point, course in ghosts:
        if valid([point[0] + course[0], point[1] + course[1]]):
            point[0] += course[0]
            point[1] += course[1]
        else:
            options = [[5, 0], [-5, 0], [0, 5], [0, -5]]
            course[:] = random.choice(options)

        path.up()
        path.goto(point[0] + 10, point[1] + 10)
        path.dot(20, "red")

    path.up()
    path.goto(pacman[0] + 10, pacman[1] + 10)
    path.dot(20, "yellow")

    update()

    for point, _ in ghosts:
        if abs(pacman[0] - point[0]) < 20 and abs(pacman[1] - point[1]) < 20:
            return

    ontimer(move, 100)


def change(x, y):
    """Cambia la dirección de Pacman si la siguiente posición es válida."""
    if valid([pacman[0] + x, pacman[1] + y]):
        aim[0] = x
        aim[1] = y


# Configuración inicial del juego
hideturtle()
tracer(False)
writer.goto(160, 160)
writer.color("white")
writer.write(score, font=FONT)

listen()
onkey(lambda: change(5, 0), "Right")
onkey(lambda: change(-5, 0), "Left")
onkey(lambda: change(0, 5), "Up")
onkey(lambda: change(0, -5), "Down")

world()
move()
turtle.done()