import random

# Configurações da janela
WIDTH = 800
HEIGHT = 400
TITLE = "Alien Platformer 👽"

# Ator principal
alien = Actor("alien.png")  # imagem: alien.png (na pasta images)
alien.x = 100
alien.y = 300
alien.vy = 0  # velocidade vertical
alien.on_ground = False

# Plataformas (chão e outras)
platforms = [
    Rect((0, 380), (WIDTH, 20)),  # chão
    Rect((200, 300), (100, 10)),
    Rect((400, 250), (100, 10)),
    Rect((600, 200), (100, 10))
]

# Lista de inimigos
enemies = []

# Variáveis do jogo
gravity = 0.5
game_over = False
score = 0


def spawn_enemy():
    """Cria um inimigo que se move da direita para a esquerda."""
    enemy = Actor("enemy")  # imagem: enemy.png
    enemy.x = WIDTH + 50
    enemy.y = random.choice([300, 250, 200])
    enemy.speed = random.randint(2, 4)
    enemies.append(enemy)


def draw():
    screen.fill((20, 20, 40))  # fundo escuro
    screen.draw.text(f"Score: {score}", (10, 10), color="white")

    for platform in platforms:
        screen.draw.filled_rect(platform, (50, 150, 50))

    alien.draw()

    for enemy in enemies:
        enemy.draw()

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="red")


def update():
    global game_over, score

    if game_over:
        return

    # Gravidade
    alien.vy += gravity
    alien.y += alien.vy

    # Movimento lateral
    if keyboard.left:
        alien.x -= 4
    if keyboard.right:
        alien.x += 4

    # Colisão com plataformas
    alien.on_ground = False
    for platform in platforms:
        if alien.colliderect(platform) and alien.vy >= 0:
            alien.y = platform.y - 40  # altura do alien
            alien.vy = 0
            alien.on_ground = True

    # Limites da tela
    if alien.x < 0:
        alien.x = 0
    if alien.x > WIDTH:
        alien.x = WIDTH

    # Movimentação dos inimigos
    for enemy in enemies:
        enemy.x -= enemy.speed
        if enemy.x < -50:
            enemies.remove(enemy)
            score += 1  # ganha ponto se escapar do inimigo
        # colisão com alien
        if alien.colliderect(enemy):
            game_over = True

    # Gerar inimigos aleatoriamente
    if random.randint(0, 100) < 2:
        spawn_enemy()


def on_key_down(key):
    if key == keys.SPACE and alien.on_ground:
        alien.vy = -10  # pulo
    if key == keys.R and game_over:
        restart_game()


def restart_game():
    """Reinicia o jogo."""
    global game_over, score, enemies
    game_over = False
    score = 0
    enemies = []
    alien.x = 100
    alien.y = 300
    alien.vy = 0
    alien.on_ground = False
