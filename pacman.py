"""Pacman, classic arcade game.

Exercises

1. Change the board.
2. Change the number of ghosts.
3. Change where pacman starts.
4. Make the ghosts faster/slower.
5. Make the ghosts smarter.
"""

from random import choice
import turtle as t

from freegames import floor, vector

# ----- Configuración y constantes -------------------------------------------

CELL = 20                # tamaño de la celda (px)
TIMER_MS = 70            # << más rápido que 100 ms: juego y fantasmas más ágiles
PELLET_COLOR = "gold"    # color del pellet (Sofía)
PELLET_SIZE = 6          # lado del pellet cuadrado en px (Sofía)

state = {"score": 0}
path = t.Turtle(visible=False)
writer = t.Turtle(visible=False)
aim = vector(5, 0)
pacman = vector(-40, -80)
ghosts = [
    [vector(-180, 160), vector(5, 0)],
    [vector(-180, -160), vector(0, 5)],
    [vector(100, 160), vector(0, -5)],
    [vector(100, -160), vector(-5, 0)],
]

# fmt: off
tiles = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
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


def square(x, y):
    """Draw square using path at (x, y)."""
    path.up()
    path.goto(x, y)
    path.down()
    path.begin_fill()

    for _ in range(4):
        path.forward(CELL)
        path.left(90)

    path.end_fill()


def pellet_square(x, y):
    """Draw pellet as a small gold square centered in the cell."""
    cx = x + CELL // 2
    cy = y + CELL // 2
    half = PELLET_SIZE // 2

    path.up()
    path.goto(cx - half, cy - half)
    path.down()
    path.color(PELLET_COLOR)
    path.begin_fill()
    for _ in range(4):
        path.forward(PELLET_SIZE)
        path.left(90)
    path.end_fill()
    path.color("blue")  # restore path color for walls


def offset(point):
    """Return offset of point in tiles."""
    x = (floor(point.x, CELL) + 200) / CELL
    y = (180 - floor(point.y, CELL)) / CELL
    index = int(x + y * 20)
    return index


def valid(point):
    """Return True if point is valid in tiles."""
    index = offset(point)
    if tiles[index] == 0:
        return False

    index = offset(point + (CELL - 1))
    if tiles[index] == 0:
        return False

    return point.x % CELL == 0 or point.y % CELL == 0


def world():
    """Draw world using path (walls + pellets)."""
    t.bgcolor("black")
    path.color("blue")

    for index, tile in enumerate(tiles):
        if tile > 0:
            x = (index % 20) * CELL - 200
            y = 180 - (index // 20) * CELL
            square(x, y)

            if tile == 1:
                pellet_square(x, y)


def move():
    """Move pacman and all ghosts; update score and collisions."""
    writer.undo()
    writer.write(state["score"])

    t.clear()

    if valid(pacman + aim):
        pacman.move(aim)

    index = offset(pacman)

    if tiles[index] == 1:
        tiles[index] = 2
        state["score"] += 1
        x = (index % 20) * CELL - 200
        y = 180 - (index // 20) * CELL
        square(x, y)

    t.up()
    t.goto(pacman.x + CELL // 2, pacman.y + CELL // 2)
    t.dot(CELL, "yellow")

    for point, course in ghosts:
        if valid(point + course):
            point.move(course)
        else:
            options = [
                vector(5, 0),
                vector(-5, 0),
                vector(0, 5),
                vector(0, -5),
            ]
            plan = choice(options)
            course.x = plan.x
            course.y = plan.y

        t.up()
        t.goto(point.x + CELL // 2, point.y + CELL // 2)
        t.dot(CELL, "red")

    t.update()

    for point, _ in ghosts:
        if abs(pacman - point) < CELL:
            return

    # Fantasmas/juego más rápidos: menor intervalo de actualización
    t.ontimer(move, TIMER_MS)


def change(x, y):
    """Change pacman aim if valid."""
    if valid(pacman + vector(x, y)):
        aim.x = x
        aim.y = y


# ----- Setup de Turtle -------------------------------------------------------

t.setup(420, 420, 370, 0)
t.hideturtle()
t.tracer(False)
writer.goto(160, 160)
writer.color("white")
writer.write(state["score"])
t.listen()
t.onkey(lambda: change(5, 0), "Right")
t.onkey(lambda: change(-5, 0), "Left")
t.onkey(lambda: change(0, 5), "Up")
t.onkey(lambda: change(0, -5), "Down")
world()
move()
t.done()
