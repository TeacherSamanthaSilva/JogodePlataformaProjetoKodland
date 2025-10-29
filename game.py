import pgzrun
import pygame
import random
import math

# ===================== #
# --- GAME SETTINGS --- #
# ===================== #

WIDTH = 800
HEIGHT = 600
GRAVITY = 0.5
JUMP_FORCE = -10

# ===================== #
# --- GAME VARIABLES --- #
# ===================== #

background_music = "musica"
pygame.mixer.init()
pygame.mixer.music.load("sounds/musica.ogg")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


# ===================== #
# --- HERO CLASS --- #
# ===================== #

class Hero:
    """Main player character that can move, jump, and animate."""

    def __init__(self, x, y):
        self.sprites = [f"alien{i}" for i in range(1, 10)]
        self.actor = Actor(self.sprites[0], (x, y))
        self.velocity_y = 0
        self.on_ground = False
        self.frame_index = 0
        self.frame_timer = 0
        self.direction = 1  # 1 right, -1 left

    def update(self):
        """Update hero movement and gravity."""
        self.apply_gravity()
        self.handle_input()
        self.animate()
        self.actor.angle = math.sin(pygame.time.get_ticks() / 500) * 2  # breathing animation

    def apply_gravity(self):
        """Apply gravity and handle floor collision."""
        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y

        if self.actor.y > HEIGHT - 50:
            self.actor.y = HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True

    def handle_input(self):
        """Handle keyboard input for movement and jump."""
        if keyboard.left:
            self.actor.x -= 4
            self.direction = -1
        if keyboard.right:
            self.actor.x += 4
            self.direction = 1
        if keyboard.space and self.on_ground:
            self.velocity_y = JUMP_FORCE
            self.on_ground = False
            sounds.jump.play()

    def animate(self):
        """Animate hero movement and idle frames."""
        self.frame_timer += 1
        if self.frame_timer >= 6:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.sprites)
            self.actor.image = self.sprites[self.frame_index]

        self.actor.angle = math.sin(pygame.time.get_ticks() / 400) * 2
        self.actor.flip_x = self.direction == -1

    def draw(self):
        """Draw hero on screen."""
        self.actor.draw()


# ===================== #
# --- ENEMY CLASS --- #
# ===================== #

class Enemy:
    """Enemy that moves and animates within a defined area."""

    def __init__(self, name, x, y, left_limit, right_limit, speed=2):
        self.sprites = [f"{name}{i}" for i in range(1, 10)]
        self.actor = Actor(self.sprites[0], (x, y))
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.speed = speed
        self.direction = 1
        self.frame_index = 0
        self.frame_timer = 0

    def update(self):
        """Move and animate the enemy."""
        self.actor.x += self.speed * self.direction
        if self.actor.x < self.left_limit or self.actor.x > self.right_limit:
            self.direction *= -1

        self.animate()

    def animate(self):
        """Cycle through animation frames."""
        self.frame_timer += 1
        if self.frame_timer >= 8:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.sprites)
            self.actor.image = self.sprites[self.frame_index]
            self.actor.flip_x = self.direction == -1

    def draw(self):
        """Draw enemy on screen."""
        self.actor.draw()


# ===================== #
# --- SETUP OBJECTS --- #
# ===================== #

alien = Hero(100, HEIGHT - 50)
enemies = [
    Enemy("purple_enemy", 300, HEIGHT - 50, 250, 500, speed=2),
    Enemy("pink_enemy", 600, HEIGHT - 50, 550, 750, speed=3),
    Enemy("bee", 400, HEIGHT - 200, 350, 700, speed=4)
]

# ===================== #
# --- GAME STATES --- #
# ===================== #

def update():
    """Main update loop controlling game states."""
    global game_state
    if game_state == "menu":
        pass
    elif game_state == "playing":
        alien.update()
        for enemy in enemies:
            enemy.update()
        check_collisions()

def draw():
    """Draw elements depending on the current state."""
    screen.clear()
    if game_state == "menu":
        screen.draw.text("Press SPACE to Start", center=(WIDTH / 2, HEIGHT / 2), fontsize=50, color="white")
    elif game_state == "playing":
        alien.draw()
        for enemy in enemies:
            enemy.draw()

def check_collisions():
    """Detect collisions between hero and enemies."""
    for enemy in enemies:
        if alien.actor.colliderect(enemy.actor):
            sounds.explosion.play()
            reset_game()

def reset_game():
    """Reset hero and enemies positions."""
    global game_state
    alien.actor.pos = (100, HEIGHT - 50)
    for i, enemy in enumerate(enemies):
        enemy.actor.x = 300 + (i * 200)
    game_state = "menu"

def on_key_down(key):
    """Handle key presses for state transitions."""
    global game_state
    if game_state == "menu" and key == keys.SPACE:
        game_state = "playing"

# ===================== #
# --- RUN GAME --- #
# ===================== #

pgzrun.go()
