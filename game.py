import random
import pgzrun
import math

# Configuracoes da janela
WIDTH = 800
HEIGHT = 400
TITLE = "Alien Platformer"

# Ator principal
alien = Actor("alien")
alien.x = 100
alien.y = 300
alien.vy = 0
alien.on_ground = False

# Plataformas espalhadas
platforms = [
    Rect((0, 380), (WIDTH, 20)),      # chao
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

# Listas de inimigos, abelhas, bombas, moedas e explosoes
enemies = []
bees = []
bombs = []
coins = []
explosions = []

# Variaveis do jogo
gravity = 0.5
game_over = False
victory = False
score = 0
MAX_LIVES = 3
lives = MAX_LIVES

# Timers de spawn (em frames)
enemy_timer = 0
bee_timer = 0
coin_timer = 0

# Intervalos de spawn (em frames)
ENEMY_INTERVAL = 120  # inimigo a cada 2 segundos (60fps)
BEE_INTERVAL = 180    # abelha a cada 3 segundos
COIN_INTERVAL = 300   # moeda a cada 5 segundos

# --- Funcoes de spawn ---
def spawn_enemy():
    tipo = random.choice(["enemy", "enemy2"])
    enemy = Actor(tipo)
    enemy.x = WIDTH + 50
    enemy.y = random.choice([platform.y - 40 for platform in platforms if platform.y >= 240])
    enemy.speed = random.randint(2, 4) if tipo == "enemy" else random.randint(3, 5)
    enemies.append(enemy)

def spawn_bee():
    bee = Actor("bee")
    bee.x = WIDTH + 50
    bee.y = random.randint(100, 250)
    bee.speed = random.uniform(2, 3)
    bee.oscillation = random.uniform(0, math.pi * 2)
    bees.append(bee)

def spawn_coin():
    platform = random.choice(platforms[1:])
    coin = Actor("coin")
    coin.x = random.randint(platform.left + 10, platform.right - 10)
    coin.y = platform.y - 20
    coins.append(coin)

# --- Desenho ---
def draw():
    screen.fill((20, 20, 40))
    screen.draw.text(f"Score: {score}", (10, 10), color="white")

    # Desenhar vidas
    for i in range(lives):
        screen.blit("heart", (10 + i*35, 40))  # imagem heart.png

    for platform in platforms:
        screen.draw.filled_rect(platform, (50, 150, 50))

    flag.draw()
    alien.draw()

    for enemy in enemies:
        enemy.draw()
    for bee in bees:
        bee.draw()
    for bomb in bombs:
        bomb.draw()
    for coin in coins:
        coin.draw()

    for (x, y, timer) in explosions:
        radius = 15 + (5 - timer) * 5
        screen.draw.filled_circle((x, y), radius, (255, 80, 0))

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="red")
        screen.draw.text("Press R to restart", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color="white")

    if victory:
        screen.draw.text("CONGRATS! LEVEL COMPLETE!", center=(WIDTH/2, HEIGHT/2), fontsize=50, color="yellow")
        screen.draw.text(f"Final Score: {score}", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color="white")
        screen.draw.text("Press R to restart", center=(WIDTH/2, HEIGHT/2 + 90), fontsize=25, color="white")

# --- Atualizacao ---
def update():
    global game_over, score, victory
    global enemy_timer, bee_timer, coin_timer, lives

    if game_over or victory:
        return

    # Gravidade e movimento vertical
    alien.vy += gravity
    alien.y += alien.vy

    # Movimento lateral
    if keyboard.left:
        alien.x -= 4
    if keyboard.right:
        alien.x += 4

    # Colisao com plataformas
    alien.on_ground = False
    for platform in platforms:
        if alien.colliderect(platform) and alien.vy >= 0:
            alien.y = platform.y - 40
            alien.vy = 0
            alien.on_ground = True

    alien.x = max(0, min(WIDTH, alien.x))

    # Verificar bandeira
    if alien.colliderect(flag):
        victory = True

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
                score += 1
                break
        for bee in list(bees):
            if bomb.colliderect(bee):
                explosions.append([bee.x, bee.y, 5])
                bees.remove(bee)
                bombs.remove(bomb)
                score += 1
                break

    # Atualizar explosoes
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
            lives -= 1
            enemies.remove(enemy)
            if lives <= 0:
                game_over = True

    # Movimentar abelhas
    for bee in bees:
        bee.x -= bee.speed
        bee.y += math.sin(bee.oscillation) * 2
        bee.oscillation += 0.1
        if bee.x < -50:
            bees.remove(bee)
        elif alien.colliderect(bee):
            lives -= 1
            bees.remove(bee)
            if lives <= 0:
                game_over = True

    # Coletar moedas
    for coin in list(coins):
        if alien.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Atualizar timers e spawnar inimigos, abelhas e moedas
    enemy_timer += 1
    bee_timer += 1
    coin_timer += 1

    if enemy_timer >= ENEMY_INTERVAL:
        spawn_enemy()
        enemy_timer = 0

    if bee_timer >= BEE_INTERVAL:
        spawn_bee()
        bee_timer = 0

    if coin_timer >= COIN_INTERVAL:
        spawn_coin()
        coin_timer = 0

# --- Eventos ---
def on_key_down(key):
    if key == keys.SPACE and alien.on_ground:
        alien.vy = -10
    if key == keys.Z:
        throw_bomb()
    if key == keys.R and (game_over or victory):
        restart_game()

def throw_bomb():
    bomb = Actor("bomb")
    bomb.x = alien.x + 20
    bomb.y = alien.y
    bombs.append(bomb)

def restart_game():
    global game_over, score, enemies, bees, bombs, coins, explosions, victory, lives
    global enemy_timer, bee_timer, coin_timer
    game_over = False
    victory = False
    score = 0
    lives = MAX_LIVES
    enemies = []
    bees = []
    bombs = []
    coins = []
    explosions = []
    alien.x = 100
    alien.y = 300
    alien.vy = 0
    alien.on_ground = False
    enemy_timer = 0
    bee_timer = 0
    coin_timer = 0

pgzrun.go()
