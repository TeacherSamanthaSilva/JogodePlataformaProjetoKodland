import random
import math
import pgzrun
from pgzero.actor import Actor
from pygame import Rect

# --- Configurações da janela ---
WIDTH = 800
HEIGHT = 400
TITLE = "Batalha Alien"

# --- Estado do jogo ---
game_state = "menu"  # "menu", "instructions", "playing", "game_over", "victory"
menu_options = ["Start", "Instructions", "Quit"]
selected_option = 0

# --- Variáveis do jogo ---
gravity = 0.5
MAX_LIVES = 3

# --- Classes ---
class Player(Actor):
    def __init__(self):
        super().__init__("alien")
        self.x = 100
        self.y = 300
        self.vy = 0
        self.on_ground = False
        self.lives = MAX_LIVES
        self.score = 0

class Enemy(Actor):
    def __init__(self, kind, x, y, speed):
        super().__init__(kind)
        self.x = x
        self.y = y
        self.speed = speed

class Bee(Actor):
    def __init__(self, x, y, speed, oscillation):
        super().__init__("bee")
        self.x = x
        self.y = y
        self.speed = speed
        self.oscillation = oscillation

class Bomb(Actor):
    def __init__(self, x, y):
        super().__init__("bomb")
        self.x = x
        self.y = y
        self.speed = 6

# --- Criar jogador ---
alien = Player()

# --- Plataformas ---
platforms = [
    Rect((0, 380), (WIDTH, 20)),
    Rect((100, 320), (80, 10)),
    Rect((220, 280), (80, 10)),
    Rect((350, 240), (80, 10)),
    Rect((500, 300), (100, 10)),
    Rect((650, 260), (80, 10)),
    Rect((720, 200), (60, 10)),
    Rect((400, 160), (80, 10)),
    Rect((200, 100), (80, 10))
]

# --- Bandeira ---
flag = Actor("flag")
flag.x = WIDTH - 50
flag.y = 150

# --- Listas de objetos ---
enemies = []
bees = []
bombs = []
coins = []
explosions = []

# --- Timers ---
enemy_timer = 0
bee_timer = 0
coin_timer = 0
ENEMY_INTERVAL = 120
BEE_INTERVAL = 180
COIN_INTERVAL = 300

# --- Funções de spawn ---
def spawn_enemy():
    kind = random.choice(["enemy", "enemy2"])
    enemy = Enemy(kind, WIDTH + 50, random.choice([p.y - 40 for p in platforms if p.y >= 240]),
                  random.randint(2, 4) if kind == "enemy" else random.randint(3, 5))
    enemies.append(enemy)

def spawn_bee():
    bee = Bee(WIDTH + 50, random.randint(100, 250), random.uniform(2, 3), random.uniform(0, math.pi*2))
    bees.append(bee)

def spawn_coin():
    platform = random.choice(platforms[1:])
    coin = Actor("coin")
    coin.x = random.randint(platform.left + 10, platform.right - 10)
    coin.y = platform.y - 20
    coins.append(coin)

# --- Função de reinício ---
def restart_game():
    global game_over, victory, enemy_timer, bee_timer, coin_timer
    global enemies, bees, bombs, coins, explosions

    game_over = False
    victory = False
    alien.lives = MAX_LIVES
    alien.score = 0
    alien.x = 100
    alien.y = 300
    alien.vy = 0
    alien.on_ground = False

    enemies = []
    bees = []
    bombs = []
    coins = []
    explosions = []

    enemy_timer = 0
    bee_timer = 0
    coin_timer = 0

# --- Funções de controle ---
def start_game():
    global game_state
    game_state = "playing"
    restart_game()
    sounds.musica.play(-1)

def throw_bomb():
    bomb = Bomb(alien.x + 20, alien.y)
    bombs.append(bomb)
    sounds.bomb.play()

# --- Eventos de teclado ---
def on_key_down(key):
    global selected_option, game_state

    if game_state == "menu":
        if key == keys.UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif key == keys.DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif key == keys.RETURN:
            execute_menu_option(selected_option)
    elif game_state == "instructions":
        if key == keys.B:
            game_state = "menu"
    elif game_state == "playing":
        if key == keys.SPACE and alien.on_ground:
            alien.vy = -10
            sounds.jump.play()
        if key == keys.Z:
            throw_bomb()
        if key == keys.R and (game_over or victory):
            restart_game()

# --- Eventos de mouse ---
def on_mouse_down(pos):
    if game_state == "menu":
        for i, option in enumerate(menu_options):
            button_rect = Rect((WIDTH/2 - 100, 175 + i*50), (200, 40))
            if button_rect.collidepoint(pos):
                execute_menu_option(i)

def execute_menu_option(option_index):
    option = menu_options[option_index]
    global game_state
    if option == "Start":
        start_game()
    elif option == "Instructions":
        game_state = "instructions"
    elif option == "Quit":
        quit()

# --- Atualização ---
def update():
    global game_over, victory, enemy_timer, bee_timer, coin_timer

    if game_state != "playing" or game_over or victory:
        return

    # Gravidade e movimento
    alien.vy += gravity
    alien.y += alien.vy

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

    alien.x = max(0, min(WIDTH, alien.x))

    # Verificar vitória
    if alien.colliderect(flag) and not victory:
        victory = True
        sounds.musica.stop()
        sounds.victory.play()

    # Atualizar bombas
    for bomb in list(bombs):
        bomb.x += bomb.speed
        if bomb.x > WIDTH + 50:
            bombs.remove(bomb)
            continue
        for enemy in list(enemies):
            if bomb.colliderect(enemy):
                explosions.append([enemy.x, enemy.y, 5])
                enemies.remove(enemy)
                bombs.remove(bomb)
                alien.score += 1
                break
        for bee in list(bees):
            if bomb.colliderect(bee):
                explosions.append([bee.x, bee.y, 5])
                bees.remove(bee)
                bombs.remove(bomb)
                alien.score += 1
                break

    # Atualizar explosões
    for exp in list(explosions):
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)

    # Atualizar inimigos
    for enemy in list(enemies):
        enemy.x -= enemy.speed
        if enemy.x < -50:
            enemies.remove(enemy)
            alien.score += 1
        elif alien.colliderect(enemy):
            alien.lives -= 1
            enemies.remove(enemy)
            if alien.lives <= 0:
                game_over_func()

    # Atualizar abelhas
    for bee in list(bees):
        bee.x -= bee.speed
        bee.y += math.sin(bee.oscillation) * 2
        bee.oscillation += 0.1
        if bee.x < -50:
            bees.remove(bee)
        elif alien.colliderect(bee):
            alien.lives -= 1
            bees.remove(bee)
            if alien.lives <= 0:
                game_over_func()

    # Coletar moedas
    for coin in list(coins):
        if alien.colliderect(coin):
            coins.remove(coin)
            alien.score += 1
            sounds.coin.play()

    # Timers
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

def game_over_func():
    global game_over
    game_over = True
    sounds.musica.stop()
    sounds.gameover.play()

# --- Desenho ---
def draw():
    screen.fill((20, 20, 40))

    if game_state == "menu":
        screen.draw.text("ALIEN PLATFORMER", center=(WIDTH/2, 100), fontsize=60, color="yellow")
        for i, option in enumerate(menu_options):
            color = "red" if i == selected_option else "white"
            screen.draw.text(option, center=(WIDTH/2, 200 + i*50), fontsize=40, color=color)
        screen.draw.text("Use UP/DOWN or click to select", center=(WIDTH/2, 350), fontsize=20, color="white")

    elif game_state == "instructions":
        screen.draw.text("INSTRUCTIONS", center=(WIDTH/2, 80), fontsize=50, color="yellow")
        screen.draw.text("Arrow keys: Move left/right", center=(WIDTH/2, 150), fontsize=30, color="white")
        screen.draw.text("SPACE: Jump", center=(WIDTH/2, 200), fontsize=30, color="white")
        screen.draw.text("Z: Throw bomb", center=(WIDTH/2, 250), fontsize=30, color="white")
        screen.draw.text("Collect coins, avoid enemies!", center=(WIDTH/2, 300), fontsize=25, color="white")
        screen.draw.text("Press B to go back", center=(WIDTH/2, 350), fontsize=20, color="white")

    elif game_state in ["playing", "game_over", "victory"]:
        screen.draw.text(f"Score: {alien.score}", (10, 10), color="white")

        # Vidas
        for i in range(alien.lives):
            screen.blit("heart", (10 + i*35, 40))

        # Plataformas
        for platform in platforms:
            screen.draw.filled_rect(platform, (50, 150, 50))

        # Bandeira e alien
        flag.draw()
        alien.draw()

        # Inimigos, abelhas, bombas, moedas
        for enemy in enemies:
            enemy.draw()
        for bee in bees:
            bee.draw()
        for bomb in bombs:
            bomb.draw()
        for coin in coins:
            coin.draw()

        # Explosões
        for (x, y, timer) in explosions:
            radius = 15 + (5 - timer) * 5
            screen.draw.filled_circle((x, y), radius, (255, 80, 0))

        # Game over / vitória
        if game_over:
            screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=60, color="red")
            screen.draw.text("Press R to restart", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color="white")
        if victory:
            screen.draw.text("CONGRATS! LEVEL COMPLETE!", center=(WIDTH/2, HEIGHT/2), fontsize=50, color="yellow")
            screen.draw.text(f"Final Score: {alien.score}", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=30, color="white")
            screen.draw.text("Press R to restart", center=(WIDTH/2, HEIGHT/2 + 90), fontsize=25, color="white")

# --- Iniciar o jogo ---
pgzrun.go()
