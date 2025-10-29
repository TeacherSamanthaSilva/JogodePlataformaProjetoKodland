import random
import pgzrun

# Configurações da janela
WIDTH = 800
HEIGHT = 400
TITLE = "Alien Platformer 👽💣🪙"

# Ator principal
alien = Actor("alien")
alien.x = 100
alien.y = 300
alien.vy = 0
alien.on_ground = False

# Plataformas espalhadas
platforms = [
    Rect((0, 380), (WIDTH, 20)),      # chão
    Rect((100, 320), (80, 10)),
    Rect((220, 280), (80, 10)),
    Rect((350, 240), (80, 10)),
    Rect((500, 300), (100, 10)),
    Rect((650, 260), (80, 10)),
    Rect((720, 200), (60, 10)),
    Rect((400, 160), (80, 10)),
    Rect((200, 100), (80, 10))
]

# Bandeira do final da fase
flag = Actor("flag")
flag.x = WIDTH - 50
flag.y = 150

# Listas de inimigos, bombas, moedas e e
