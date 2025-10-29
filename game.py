import random
import pgzrun

# Configurações da janela
WIDTH = 800
HEIGHT = 400
TITLE = "Alien Platformer 👽💣"

# Ator principal
alien = Actor("alien")
alien.x = 100
alien.y = 300
alien.vy = 0
alien.on_ground = False

# Plataformas
platforms = [
    Rect((0, 380), (WIDTH, 20)),  # chão
    Rect((200, 300), (100, 10)),
    Rect((400, 250), (100, 10)),
    Rect((600, 200), (100, 10))
]

# Listas de inimigos e bombas
enemies = []
bombs = []
explosions = []

# Variáveis do jogo
gravity = 0.5
game_over = False
score = 0


def spawn_enemy():
    enemy = Actor("enemy")
    enemy.x = WIDTH + 50
    enemy.y = random.choice([300, 250, 200])
    enemy.speed = random.randint(2, 4)
    enemies.append(enemy)


def draw():
    screen.fill((20, 20, 40))
    screen.draw.text(f"Score: {score}", (10, 10), color="white")

    for platform in platforms:
        screen.draw.filled_rect(platform, (50, 150, 50))

    alien.draw()

    for enemy in enemies:
        enemy.draw()

    for bomb in bombs:
        bomb.draw()

    for (x, y, timer) in explosions:
        radius = 15 + (5 - timer) * 5
        color = (255, 80, 0)
        screen.draw.filled_circle((x, y), radius, color)

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="red")
        screen.draw.text("Pressione R para reiniciar", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color="white")


def update():
    global game_over, score

    if game_over:
        return

    # Gravidade e movimento vertical
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
            alien.y = platform.y - 40
            alien.vy = 0
            alien.on_ground = True

    # Limites da tela
    if alien.x < 0:
        alien.x = 0
    if alien.x > WIDTH:
        alien.x = WIDTH

    # Atualizar bombas
    for bomb in list(bombs):
        bomb.x += 6
        if bomb.x > WIDTH + 50:
            bombs.remove(bomb)
            continue
        for enemy in list(enemies):
            if bomb.colliderect(enemy):
                explosions.append([enemy.x, enemy.y, 5])
                enemies.remove(enemy)
                bombs.remove(bomb)
                score += 10
                break

    # Atualizar explosões
    for exp in list(explosions):
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)

    # Movimentar inimigos
    for enemy in list(enemies):
        enemy.x -= enemy.speed
        if enemy.x < -50:
            enemies.remove(enemy)
            score += 1
        elif alien.colliderect(enemy):
            game_over = True

    # Gerar inimigos aleatoriamente
    if random.randint(0, 100) < 2:
        spawn_enemy()


def on_key_down(key):
    if key == keys.SPACE and alien.on_ground:
        alien.vy = -10  # pulo
    if key == keys.Z:
        throw_bomb()  # lança bomba
    if key == keys.R and game_over:
        restart_game()


def throw_bomb():
    bomb = Actor("bomb")
    bomb.x = alien.x + 20
    bomb.y = alien.y
    bombs.append(bomb)


def restart_game():
    global game_over, score, enemies, bombs, explosions
    game_over = False
    score = 0
    enemies = []
    bombs = []
    explosions = []
    alien.x = 100
    alien.y = 300
    alien.vy = 0
    alien.on_ground = False


pgzrun.go()
