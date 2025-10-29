import random
import math
import pgzrun
from pygame import Rect

# -------------------------
# Configurations
# -------------------------
WIDTH = 800
HEIGHT = 400
TITLE = "Batalha Alien"  # Título atualizado

# -------------------------
# Global Variables
# -------------------------
score = 0
MAX_LIVES = 3
lives = MAX_LIVES
gravity = 0.5

# Sound toggle
music_on = True
sounds_on = True

game_state = "menu"  # "menu", "playing", "game_over", "victory"

# -------------------------
# Classes
# -------------------------
class Character:
    def __init__(self, images, x, y):
        self.images = images  # List of sprite images
        self.frame = 0
        self.actor = Actor(self.images[self.frame])
        self.actor.x = x
        self.actor.y = y
        self.vy = 0
        self.on_ground = False
        self.animation_counter = 0

    def update_sprite(self):
        self.animation_counter += 1
        if self.animation_counter % 5 == 0:
            self.frame = (self.frame + 1) % len(self.images)
            self.actor.image = self.images[self.frame]

    def apply_gravity(self):
        self.vy += gravity
        self.actor.y += self.vy

    def check_platforms(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.actor.colliderect(platform) and self.vy >= 0:
                self.actor.y = platform.y - 40
                self.vy = 0
                self.on_ground = True

class Enemy:
    def __init__(self, images, x, y, speed):
        self.images = images
        self.frame = 0
        self.actor = Actor(self.images[self.frame])
        self.actor.x = x
        self.actor.y = y
        self.speed = speed
        self.animation_counter = 0

    def move(self):
        self.actor.x -= self.speed

    def update_sprite(self):
        self.animation_counter += 1
        if self.animation_counter % 10 == 0:
            self.frame = (self.frame + 1) % len(self.images)
            self.actor.image = self.images[self.frame]

class Bee(Enemy):
    def __init__(self, images, x, y, speed):
        super().__init__(images, x, y, speed)
        self.oscillation = random.uniform(0, math.pi*2)

    def move(self):
        self.actor.x -= self.speed
        self.actor.y += math.sin(self.oscillation) * 2
        self.oscillation += 0.1

class Bomb:
    def __init__(self, x, y):
        self.actor = Actor("bomb")
        self.actor.x = x
        self.actor.y = y

    def move(self):
        self.actor.x += 6

# -------------------------
# Platforms and Objects
# -------------------------
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

flag = Actor("flag")
flag.x = WIDTH - 50
flag.y = 150

# -------------------------
# Game Objects
# -------------------------
alien = Character(["alien1", "alien2", "alien3"], 100, 300)
enemies = []
bees = []
bombs = []
coins = []
explosions = []

# Timers
enemy_timer = 0
bee_timer = 0
coin_timer = 0
ENEMY_INTERVAL = 120
BEE_INTERVAL = 180
COIN_INTERVAL = 300

# -------------------------
# Menu Buttons
# -------------------------
menu_buttons = [
    {"text": "Start Game", "rect": Rect((WIDTH/2-100, 150, 200, 50))},
    {"text": "Toggle Music", "rect": Rect((WIDTH/2-100, 220, 200, 50))},
    {"text": "Quit", "rect": Rect((WIDTH/2-100, 290, 200, 50))}
]

# -------------------------
# Functions
# -------------------------
def spawn_enemy():
    enemy_type = random.choice(["enemy", "enemy2"])
    x = WIDTH + 50
    y = random.choice([platform.y - 40 for platform in platforms if platform.y >= 240])
    speed = random.randint(2, 4) if enemy_type == "enemy" else random.randint(3, 5)
    enemies.append(Enemy([enemy_type + "1", enemy_type + "2"], x, y, speed))

def spawn_bee():
    x = WIDTH + 50
    y = random.randint(100, 250)
    speed = random.uniform(2, 3)
    bees.append(Bee(["bee1", "bee2"], x, y, speed))

def spawn_coin():
    platform = random.choice(platforms[1:])
    coin = Actor("coin")
    coin.x = random.randint(platform.left + 10, platform.right - 10)
    coin.y = platform.y - 20
    coins.append(coin)

def throw_bomb():
    bomb = Bomb(alien.actor.x + 20, alien.actor.y)
    bombs.append(bomb)
    if sounds_on:
        sounds.bomb.play()

def restart_game():
    global enemies, bees, bombs, coins, explosions
    global score, lives, enemy_timer, bee_timer, coin_timer
    global game_state

    score = 0
    lives = MAX_LIVES
    enemies = []
    bees = []
    bombs = []
    coins = []
    explosions = []
    enemy_timer = 0
    bee_timer = 0
    coin_timer = 0
    alien.actor.x = 100
    alien.actor.y = 300
    alien.vy = 0
    alien.on_ground = False
    game_state = "playing"

# -------------------------
# Draw
# -------------------------
def draw():
    screen.fill((20, 20, 40))

    if game_state == "menu":
        screen.draw.text("BATALHA ALIEN", center=(WIDTH/2, 80), fontsize=60, color="yellow")
        for btn in menu_buttons:
            screen.draw.filled_rect(btn["rect"], (100, 100, 100))
            screen.draw.text(btn["text"], center=btn["rect"].center, fontsize=30, color="white")
    elif game_state == "playing":
        # Platforms
        for platform in platforms:
            screen.draw.filled_rect(platform, (50, 150, 50))

        # Flag
        flag.draw()

        # Alien
        alien.actor.draw()

        # Enemies
        for enemy in enemies:
            enemy.actor.draw()
        for bee in bees:
            bee.actor.draw()

        # Bombs
        for bomb in bombs:
            bomb.actor.draw()

        # Coins
        for coin in coins:
            coin.draw()

        # Score and lives
        screen.draw.text(f"Score: {score}", (10, 10), color="white")
        for i in range(lives):
            screen.blit("heart", (10 + i*35, 40))

        # Explosions
        for exp in list(explosions):
            radius = 15 + (5 - exp[2]) * 5
            screen.draw.filled_circle((exp[0], exp[1]), radius, (255, 80, 0))

# -------------------------
# Update
# -------------------------
def update():
    global enemy_timer, bee_timer, coin_timer, score, lives, game_state

    if game_state != "playing":
        return

    # Alien movement
    alien.apply_gravity()
    if keyboard.left:
        alien.actor.x -= 4
    if keyboard.right:
        alien.actor.x += 4
    alien.check_platforms(platforms)
    alien.update_sprite()

    # Victory
    if alien.actor.colliderect(flag):
        game_state = "victory"
        if music_on:
            sounds.musica.stop()
        if sounds_on:
            sounds.victory.play()

    # Bombs
    for bomb in list(bombs):
        bomb.move()
        if bomb.actor.x > WIDTH + 50:
            bombs.remove(bomb)
        for enemy in list(enemies):
            if bomb.actor.colliderect(enemy.actor):
                explosions.append([enemy.actor.x, enemy.actor.y, 5])
                enemies.remove(enemy)
                bombs.remove(bomb)
                score += 1
        for bee in list(bees):
            if bomb.actor.colliderect(bee.actor):
                explosions.append([bee.actor.x, bee.actor.y, 5])
                bees.remove(bee)
                bombs.remove(bomb)
                score += 1

    # Update enemies
    for enemy in enemies:
        enemy.move()
        enemy.update_sprite()
        if alien.actor.colliderect(enemy.actor):
            lives -= 1
            enemies.remove(enemy)
            if lives <= 0:
                game_state = "game_over"
                if music_on:
                    sounds.musica.stop()
                if sounds_on:
                    sounds.gameover.play()

    for bee in bees:
        bee.move()
        bee.update_sprite()
        if alien.actor.colliderect(bee.actor):
            lives -= 1
            bees.remove(bee)
            if lives <= 0:
                game_state = "game_over"
                if music_on:
                    sounds.musica.stop()
                if sounds_on:
                    sounds.gameover.play()

    # Coins
    for coin in list(coins):
        if alien.actor.colliderect(coin):
            coins.remove(coin)
            score += 1
            if sounds_on:
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

# -------------------------
# Mouse Input
# -------------------------
def on_mouse_down(pos):
    global music_on, sounds_on, game_state
    if game_state == "menu":
        for btn in menu_buttons:
            if btn["rect"].collidepoint(pos):
                if btn["text"] == "Start Game":
                    restart_game()
                    if music_on:
                        sounds.musica.play(-1)
                elif btn["text"] == "Toggle Music":
                    music_on = not music_on
                    if music_on:
                        sounds.musica.play(-1)
                    else:
                        sounds.musica.stop()
                elif btn["text"] == "Quit":
                    exit()

# -------------------------
# Keyboard Input
# -------------------------
def on_key_down(key):
    if game_state == "playing":
        if key == keys.SPACE and alien.on_ground:
            alien.vy = -10
            if sounds_on:
                sounds.jump.play()
        if key == keys.Z:
            throw_bomb()
        if key == keys.R and game_state in ["game_over", "victory"]:
            restart_game()

# -------------------------
# Run Game
# -------------------------
pgzrun.go()
