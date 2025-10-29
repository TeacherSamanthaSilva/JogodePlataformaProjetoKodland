import random
import pgzrun
import math

# --- Configurações da janela ---
WIDTH = 800
HEIGHT = 400
TITLE = "Alien Platformer"

# --- Estado do jogo ---
game_state = "menu"
music_on = True
sounds_on = True

# --- Menu ---
menu_buttons = {
    "Start": Rect((WIDTH//2 - 100, 150), (200, 50)),
    "Music": Rect((WIDTH//2 - 100, 220), (200, 50)),
    "Quit": Rect((WIDTH//2 - 100, 290), (200, 50))
}

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

# --- Variáveis ---
gravity = 0.5
score = 0
MAX_LIVES = 3
lives = MAX_LIVES
enemy_timer = 0
bee_timer = 0
coin_timer = 0

ENEMY_INTERVAL = 120
BEE_INTERVAL = 180
COIN_INTERVAL = 300

# --- Classes ---
class Alien:
    def __init__(self):
        self.actor = Actor("alien")
        self.actor.x = 100
        self.actor.y = 300
        self.vy = 0
        self.on_ground = False
        self.lives = MAX_LIVES

    def update(self):
        self.vy += gravity
        self.actor.y += self.vy

        if keyboard.left:
            self.actor.x -= 4
        if keyboard.right:
            self.actor.x += 4

        self.on_ground = False
        for platform in platforms:
            if self.actor.colliderect(platform) and self.vy >= 0:
                self.actor.y = platform.y - 40
                self.vy = 0
                self.on_ground = True

        self.actor.x = max(0, min(WIDTH, self.actor.x))

    def jump(self):
        if self.on_ground:
            self.vy = -10
            if sounds_on:
                sounds.jump.play()

    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self, tipo, platform):
        self.actor = Actor(tipo)
        self.platform = platform
        self.actor.x = platform.left + 20
        self.actor.y = platform.y - 40
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(2, 4) if tipo == "enemy" else random.randint(3, 5)

    def update(self):
        self.actor.x += self.speed * self.direction
        if self.actor.x < self.platform.left + 10:
            self.actor.x = self.platform.left + 10
            self.direction *= -1
        elif self.actor.x > self.platform.right - 10:
            self.actor.x = self.platform.right - 10
            self.direction *= -1

    def draw(self):
        self.actor.draw()


class Bee:
    def __init__(self):
        self.actor = Actor("bee")
        self.x_min = 400
        self.x_max = 700
        self.y_min = 100
        self.y_max = 250
        self.actor.x = random.randint(self.x_min, self.x_max)
        self.actor.y = random.randint(self.y_min, self.y_max)
        self.speed = random.uniform(2, 3)
        self.oscillation = random.uniform(0, math.pi * 2)
        self.direction = random.choice([-1, 1])

    def update(self):
        self.actor.x += self.speed * self.direction
        self.actor.y += math.sin(self.oscillation) * 2
        self.oscillation += 0.1

        if self.actor.x < self.x_min:
            self.actor.x = self.x_min
            self.direction *= -1
        elif self.actor.x > self.x_max:
            self.actor.x = self.x_max
            self.direction *= -1
        if self.actor.y < self.y_min:
            self.actor.y = self.y_min
        elif self.actor.y > self.y_max:
            self.actor.y = self.y_max

    def draw(self):
        self.actor.draw()


class Bomb:
    def __init__(self, x, y):
        self.actor = Actor("bomb")
        self.actor.x = x + 20
        self.actor.y = y
        if sounds_on:
            sounds.bomb.play()

    def update(self):
        self.actor.x += 6

    def draw(self):
        self.actor.draw()


class Coin:
    def __init__(self, platform):
        self.actor = Actor("coin")
        self.actor.x = random.randint(platform.left + 10, platform.right - 10)
        self.actor.y = platform.y - 20

    def draw(self):
        self.actor.draw()


# --- Inicialização do jogo ---
alien = Alien()
enemies = []
bees = []
bombs = []
coins = []
explosions = []

game_over = False
victory = False


# --- Funções de spawn ---
def spawn_enemy():
    platform = random.choice([p for p in platforms if p.y >= 240])
    tipo = random.choice(["enemy", "enemy2"])
    enemies.append(Enemy(tipo, platform))


def spawn_bee():
    bees.append(Bee())


def spawn_coin():
    platform = random.choice(platforms[1:])
    coins.append(Coin(platform))


# --- Funções do jogo ---
def throw_bomb():
    bombs.append(Bomb(alien.actor.x, alien.actor.y))


def restart_game():
    global game_over, victory, score, lives
    global enemies, bees, bombs, coins, explosions
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

    alien.actor.x = 100
    alien.actor.y = 300
    alien.vy = 0
    alien.on_ground = False

    enemy_timer = 0
    bee_timer = 0
    coin_timer = 0


def start_game():
    global game_state
    game_state = "playing"
    restart_game()
    if music_on:
        sounds.musica.play(-1)


# --- Eventos ---
def on_key_down(key):
    global game_state, game_over, victory
    if game_state == "instructions":
        if key == keys.B:
            game_state = "menu"
    elif game_state == "playing":
        if key == keys.SPACE:
            alien.jump()
        if key == keys.Z:
            throw_bomb()
        if key == keys.R and (game_over or victory):
            restart_game()


def on_mouse_down(pos):
    global game_state, music_on, sounds_on
    if game_state != "menu":
        return
    if menu_buttons["Start"].collidepoint(pos):
        start_game()
    elif menu_buttons["Music"].collidepoint(pos):
        music_on = not music_on
        sounds_on = music_on
        if music_on:
            sounds.musica.play(-1)
        else:
            sounds.musica.stop()
    elif menu_buttons["Quit"].collidepoint(pos):
        quit()


# --- Update ---
def update():
    global enemy_timer, bee_timer, coin_timer, game_over, victory, score, lives

    if game_state != "playing" or game_over or victory:
        return

    alien.update()

    for enemy in list(enemies):
        enemy.update()
        if alien.actor.colliderect(enemy.actor):
            lives -= 1
            enemies.remove(enemy)
            if lives <= 0:
                game_over = True
                if music_on:
                    sounds.musica.stop()
                if sounds_on:
                    sounds.gameover.play()

    for bee in list(bees):
        bee.update()
        if alien.actor.colliderect(bee.actor):
            lives -= 1
            bees.remove(bee)
            if lives <= 0:
                game_over = True
                if music_on:
                    sounds.musica.stop()
                if sounds_on:
                    sounds.gameover.play()

    for bomb in list(bombs):
        bomb.update()
        if bomb.actor.x > WIDTH + 50:
            bombs.remove(bomb)
        for enemy in list(enemies):
            if bomb.actor.colliderect(enemy.actor):
                explosions.append([enemy.actor.x, enemy.actor.y, 5])
                enemies.remove(enemy)
                bombs.remove(bomb)
                score += 1
                break
        for bee in list(bees):
            if bomb.actor.colliderect(bee.actor):
                explosions.append([bee.actor.x, bee.actor.y, 5])
                bees.remove(bee)
                bombs.remove(bomb)
                score += 1
                break

    for exp in list(explosions):
        exp[2] -= 1
        if exp[2] <= 0:
            explosions.remove(exp)

    for coin in list(coins):
        if alien.actor.colliderect(coin.actor):
            coins.remove(coin)
            score += 1
            if sounds_on:
                sounds.coin.play()

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


# --- Draw ---
def draw():
    screen.fill((20, 20, 40))

    if game_state == "menu":
        screen.draw.text("ALIEN PLATFORMER", center=(WIDTH/2, 80), fontsize=60, color="yellow")
        for name, rect in menu_buttons.items():
            if name == "Music":
                color = "green" if music_on else "red"
                text = f"Music {'ON' if music_on else 'OFF'}"
            else:
                color = "white"
                text = name
            screen.draw.filled_rect(rect, (50, 50, 50))
            screen.draw.text(text, center=rect.center, fontsize=35, color=color)

    elif game_state == "instructions":
        screen.draw.text("INSTRUCTIONS", center=(WIDTH/2, 80), fontsize=50, color="yellow")
        screen.draw.text("Arrow keys: Move left/right", center=(WIDTH/2, 150), fontsize=30, color="white")
        screen.draw.text("SPACE: Jump", center=(WIDTH/2, 200), fontsize=30, color="white")
        screen.draw.text("Z: Throw bomb", center=(WIDTH/2, 250), fontsize=30, color="white")
        screen.draw.text("Collect coins, avoid enemies!", center=(WIDTH/2, 300), fontsize=25, color="white")
        screen.draw.text("Press B to go back", center=(WIDTH/2, 350), fontsize=20, color="white")

    elif game_state in ["playing", "game_over", "victory"]:
        screen.draw.text(f"Score: {score}", (10, 10), color="white")
        for i in range(alien.lives):
            screen.blit("heart", (10 + i*35, 40))
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


# --- Iniciar jogo ---
pgzrun.go()
