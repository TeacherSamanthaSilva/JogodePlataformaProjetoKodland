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

# Plataformas espalhadas (x, y, largura, altura)
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

# Listas de inimigos, bombas, moedas e explosões
enemies = []
bombs = []
coins = []
explosions = []

# Variáveis do jogo
gravity = 0.5
game_over = False
score = 0


def spawn_enemy():
    """Cria inimigos aleatórios sobre plataformas baixas"""
    tipo = random.choice(["enemy", "enemy2"])
    enemy = Actor(tipo)
    enemy.x = WIDTH + 50
    # Escolher altura de plataformas abaixo de 320
    enemy.y = random.choice([platform.y - 40 for platform in platforms if platform.y >= 240])
    enemy.speed = random.randint(2, 4) if tipo == "enemy" else random.randint(3, 5)
    enemies.append(enemy)


def spawn_coin():
    """Cria uma moeda sobre uma plataforma aleatória"""
    platform = random.choice(platforms[1:])  # evitar chão
    coin = Actor("coin")
    coin.x = random.randint(platform.left + 10, platform.right - 10)
    coin.y = platform.y - 20
    coins.append(coin)


def draw():
    screen.fill((20, 20, 40))
    screen.draw.text(f"Score: {score}", (10, 10), color="white")

    # desenhar plataformas
    for platform in platforms:
        screen.draw.filled_rect(platform, (50, 150, 50))

    alien.draw()

    for enemy in enemies:
        enemy.draw()

    for bomb in bombs:
        bomb.draw()

    for coin in coins:
        coin.draw()

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
    alien.x = max(0, min(WIDTH, alien.x))

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

    # Coletar moedas
    for coin in list(coins):
        if alien.colliderect(coin):
            coins.remove(coin)
            score += 5

    # Gerar inimigos aleatoriamente
    if random.randint(0, 100) < 3:
        spawn_enemy()

    # Gerar moedas aleatoriamente
    if random.randint(0, 100) < 2:
        spawn_coin()


def on_key_down(key):
    if key == keys.SPACE and alien.on_ground:
        alien.vy = -10  # pulo
    if key == keys.Z:
        throw_bomb()
    if key == keys.R and game_over:
        restart_game()


def throw_bomb():
    bomb = Actor("bomb")
    bomb.x = alien.x + 20
    bomb.y = alien.y
    bombs.append(bomb)


def restart_game():
    global game_over, score, enemies, bombs, coins, explosions
    game_over = False
    score = 0
    enemies = []
    bombs = []
    coins = []
    explosions = []
    alien.x = 100
    alien.y = 300
    alien.vy = 0
    alien.on_ground = False


pgzrun.go()
