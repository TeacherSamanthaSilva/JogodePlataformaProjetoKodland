from pygame import Rect
import random
import math
import pgzrun

# --- Window ---
WIDTH = 800
HEIGHT = 400
TITLE = "Alien Battle"

# --- Constants ---
GRAVITY = 0.5
MAX_LIVES = 3

# --- Menu buttons ---
BUTTON_WIDTH = 220
BUTTON_HEIGHT = 48
button_start = Rect((WIDTH // 2 - BUTTON_WIDTH // 2, 140), (BUTTON_WIDTH, BUTTON_HEIGHT))
button_music = Rect((WIDTH // 2 - BUTTON_WIDTH // 2, 200), (BUTTON_WIDTH, BUTTON_HEIGHT))
button_quit = Rect((WIDTH // 2 - BUTTON_WIDTH // 2, 260), (BUTTON_WIDTH, BUTTON_HEIGHT))

# --- Platforms ---
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

# --- Flag (goal) ---
flag = Actor("flag")
flag.x = WIDTH - 50
flag.y = 150

# --- Game state ---
game_state = "menu"
music_on = True

# --- Entities containers ---
enemies = []
bees = []
bombs = []
coins = []
explosions = []

# --- Timers ---
enemy_timer = 0
bee_timer = 0
coin_timer = 0

ENEMY_INTERVAL = 150
BEE_INTERVAL = 220
COIN_INTERVAL = 400

# --- Score / lives ---
score = 0
lives = MAX_LIVES
game_over = False
victory = False

# --- Player class with sprite animation (alien1–9) ---
class Player:
    def __init__(self, x, y):
        # Animations: idle = 1–3, run = 4–9
        self.frames_idle = ["alien1", "alien2", "alien3"]
        self.frames_run = ["alien4", "alien5", "alien6", "alien7", "alien8", "alien9"]
        self.actor = Actor(self.frames_idle[0])
        self.x = x
        self.y = y
        self.vy = 0
        self.on_ground = False
        self.frame_index = 0
        self.frame_timer = 0
        self.facing = "right"

    @property
    def rect(self):
        return Rect((self.x - self.actor.width / 2, self.y - self.actor.height / 2),
                    (self.actor.width, self.actor.height))

    def update(self):
        # Physics
        self.vy += GRAVITY
        self.y += self.vy

        # Horizontal movement
        moving = False
        if keyboard.left:
            self.x -= 4
            self.facing = "left"
            moving = True
        if keyboard.right:
            self.x += 4
            self.facing = "right"
            moving = True

        # Bounds
        self.x = max(self.actor.width // 2, min(WIDTH - self.actor.width // 2, self.x))

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.vy >= 0 and Rect(platform.left, platform.top, platform.width, platform.height).colliderect(self.rect):
                self.y = platform.top - (self.actor.height / 2)
                self.vy = 0
                self.on_ground = True

        # Animation
        self.frame_timer += 1
        if moving:
            frames = self.frames_run
            fps = 4
        else:
            frames = self.frames_idle
            fps = 10

        if self.frame_timer >= fps:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.actor.image = frames[self.frame_index]

    def draw(self):
        self.actor.x = self.x
        self.actor.y = self.y
        self.actor.flip_x = (self.facing == "left")
        self.actor.draw()

player = Player(100, 300)

# --- Enemy classes ---
class PatrolEnemy:
    def __init__(self, x, y, left_bound, right_bound, speed=2):
        self.frames = ["enemy_walk1", "enemy_walk2"]
        self.actor = Actor(self.frames[0])
        self.x = x
        self.y = y
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.speed = speed
        self.dir = -1
        self.frame_index = 0
        self.frame_timer = 0

    @property
    def rect(self):
        return Rect((self.x - self.actor.width / 2, self.y - self.actor.height / 2),
                    (self.actor.width, self.actor.height))

    def update(self):
        self.x += self.speed * self.dir
        if self.x < self.left_bound:
            self.dir = 1
        elif self.x > self.right_bound:
            self.dir = -1
        # Animation
        self.frame_timer += 1
        if self.frame_timer >= 8:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.actor.image = self.frames[self.frame_index]

    def draw(self):
        self.actor.x = self.x
        self.actor.y = self.y
        self.actor.flip_x = (self.dir == 1)
        self.actor.draw()

class Bee:
    def __init__(self, x, y, speed=2.0):
        self.frames = ["bee1", "bee2"]
        self.actor = Actor(self.frames[0])
        self.x = x
        self.y = y
        self.speed = speed
        self.osc = random.uniform(0, math.pi * 2)
        self.frame_index = 0
        self.frame_timer = 0

    @property
    def rect(self):
        return Rect((self.x - self.actor.width / 2, self.y - self.actor.height / 2),
                    (self.actor.width, self.actor.height))

    def update(self):
        self.x -= self.speed
        self.y += math.sin(self.osc) * 2
        self.osc += 0.12
        self.frame_timer += 1
        if self.frame_timer >= 6:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.actor.image = self.frames[self.frame_index]

    def draw(self):
        self.actor.x = self.x
        self.actor.y = self.y
        self.actor.draw()

# --- Spawn functions ---
def spawn_patrol_enemy():
    platform = random.choice(platforms[1:6])
    left_bound = platform.left + 10
    right_bound = platform.right - 10
    x = random.randint(left_bound, right_bound)
    y = platform.top - 30
    speed = random.randint(1, 3)
    enemies.append(PatrolEnemy(x, y, left_bound, right_bound, speed))

def spawn_bee():
    x = WIDTH + 40
    y = random.randint(80, 260)
    bees.append(Bee(x, y, speed=random.uniform(1.5, 2.7)))

def spawn_coin():
    platform = random.choice(platforms[1:])
    coin_actor = Actor("coin")
    coin_actor.x = random.randint(platform.left + 10, platform.right - 10)
    coin_actor.y = platform.top - 20
    coins.append(coin_actor)

# --- Bomb ---
def throw_bomb():
    bomb = Actor("bomb")
    bomb.x = player.x + 20
    bomb.y = player.y
    bombs.append(bomb)
    if music_on:
        sounds.bomb.play()

# --- Game control ---
def start_game():
    global game_state
    restart_game()
    game_state = "playing"
    if music_on:
        sounds.music_track.play(-1)

def restart_game():
    global enemies, bees, bombs, coins, explosions
    global score, lives, game_over, victory
    global enemy_timer, bee_timer, coin_timer

    enemies = []
    bees = []
    bombs = []
    coins = []
    explosions = []

    score = 0
    lives = MAX_LIVES
    game_over = False
    victory = False

    player.x = 100
    player.y = 300
    player.vy = 0
    player.on_ground = False

    enemy_timer = 0
    bee_timer = 0
    coin_timer = 0

# --- Draw ---
def draw():
    screen.fill((20, 20, 40))
    if game_state == "menu":
        screen.draw.text("ALIEN PLATFORMER", center=(WIDTH/2, 60), fontsize=56, color="yellow")
        screen.draw.filled_rect(button_start, (40,40,40))
        screen.draw.text("Start", center=button_start.center, fontsize=34, color="white")
        screen.draw.filled_rect(button_music, (40,40,40))
        screen.draw.text(f"Music: {'On' if music_on else 'Off'}", center=button_music.center, fontsize=28, color="white")
        screen.draw.filled_rect(button_quit, (40,40,40))
        screen.draw.text("Quit", center=button_quit.center, fontsize=28, color="white")
    elif game_state == "instructions":
        screen.draw.text("INSTRUCTIONS", center=(WIDTH/2, 80), fontsize=48, color="yellow")
        screen.draw.text("Arrow keys: Move left/right", center=(WIDTH/2, 150), fontsize=28, color="white")
        screen.draw.text("SPACE: Jump", center=(WIDTH/2, 190), fontsize=28, color="white")
        screen.draw.text("Z: Throw bomb", center=(WIDTH/2, 230), fontsize=28, color="white")
        screen.draw.text("Reach the flag to win. Avoid enemies.", center=(WIDTH/2, 270), fontsize=24, color="white")
        screen.draw.text("Press B to go back", center=(WIDTH/2, 320), fontsize=20, color="white")
    else:
        screen.draw.text(f"Score: {score}", (10, 8), fontsize=28, color="white")
        for i in range(lives):
            screen.blit("heart", (10 + i*36, 40))
        for platform in platforms:
            screen.draw.filled_rect(platform, (50,150,50))
        flag.draw()
        player.draw()
        for e in enemies: e.draw()
        for b in bees: b.draw()
        for bomb in bombs: bomb.draw()
        for coin in coins: coin.draw()
        for (x,y,t) in list(explosions):
            radius = 12 + (5-t)*6
            screen.draw.filled_circle((x,y), radius, (255,120,20))
        if game_over:
            screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2-10), fontsize=64, color="red")
            screen.draw.text("Press R to restart", center=(WIDTH/2, HEIGHT/2+40), fontsize=28, color="white")
        if victory:
            screen.draw.text("CONGRATS! LEVEL COMPLETE!", center=(WIDTH/2, HEIGHT/2-10), fontsize=40, color="yellow")
            screen.draw.text(f"Final Score: {score}", center=(WIDTH/2, HEIGHT/2+30), fontsize=26, color="white")
            screen.draw.text("Press R to restart", center=(WIDTH/2, HEIGHT/2+70), fontsize=20, color="white")

# --- Update ---
def update():
    global enemy_timer, bee_timer, coin_timer, score, lives, game_over, victory

    if game_state != "playing" or game_over or victory:
        return

    player.update()

    # flag collision
    if player.rect.colliderect(Rect(flag.x-flag.width/2, flag.y-flag.height/2, flag.width, flag.height)):
        victory = True
        if music_on:
            sounds.music_track.stop()
            sounds.victory.play()

    # bombs
    for bomb in list(bombs):
        bomb.x += 6
        if bomb.x > WIDTH + 50: bombs.remove(bomb); continue
        for enemy in list(enemies):
            if bomb.colliderect(enemy.actor):
                explosions.append([enemy.x, enemy.y, 5])
                enemies.remove(enemy)
                bombs.remove(bomb)
                score += 1
                break

    # explosions
    for exp in list(explosions):
        exp[2] -= 1
        if exp[2] <= 0: explosions.remove(exp)

    # enemies
    for e in list(enemies):
        e.update()
        if player.rect.colliderect(e.rect):
            lives -= 1
            enemies.remove(e)
            if lives <= 0: game_over = True; sounds.music_track.stop(); sounds.gameover.play()

    # bees
    for b in list(bees):
        b.update()
        if player.rect.colliderect(b.rect):
            lives -= 1
            bees.remove(b)
            if lives <= 0: game_over = True; sounds.music_track.stop(); sounds.gameover.play()
        elif b.x < -50: bees.remove(b)

    # coins
    for coin in list(coins):
        if player.rect.colliderect(coin):
            coins.remove(coin)
            score += 1
            if music_on: sounds.coin.play()

    # spawn timers
    enemy_timer += 1
    bee_timer += 1
    coin_timer += 1

    if enemy_timer >= ENEMY_INTERVAL: spawn_patrol_enemy(); enemy_timer=0
    if bee_timer >= BEE_INTERVAL: spawn_bee(); bee_timer=0
    if coin_timer >= COIN_INTERVAL: spawn_coin(); coin_timer=0

# --- Input ---
def on_key_down(key):
    global music_on
    if game_state == "playing":
        if key == keys.SPACE and player.on_ground:
            player.vy = -10
            if music_on: sounds.jump.play()
        if key == keys.Z: throw_bomb()
        if key == keys.R and (game_over or victory): restart_game()
    elif game_state == "instructions":
        if key == keys.B: game_state = "menu"

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        if button_start.collidepoint(pos): start_game()
        elif button_music.collidepoint(pos):
            music_on = not music_on
            if not music_on: sounds.music_track.stop()
        elif button_quit.collidepoint(pos): quit()

pgzrun.go()
