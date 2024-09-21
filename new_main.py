#################### (Imports) ####################
import pygame as pg
from pygame.locals import *
from pygame import mixer
import random
import math
import uuid
import sys
import time

#################### (Program Specific Variables) ####################
pg.font.init()  # Initialize the font module

# For screen height and width
screen_width = 800
screen_height = 600
screen_mid_val = (screen_width // 2, screen_height // 2)

running = True

# FPS
FPS = 32

# Background Images
bg = pg.image.load('space-background.jpg')
bg2 = pg.image.load('space-bg.jpg')

welcome_screen = pg.image.load('Game_welcome_screen.jpg')
color_light = (170, 170, 170)

welcome_font = pg.font.SysFont('Corbel', 25)  # defining a font
show_welcome_font = welcome_font.render("Press 's' to start the game or 'q' to quit the game", True, color_light)

# Player
playerImg = pg.image.load('player6.png')
playerX = 370
playerY = 480
playerX_change = 0
playerSpeed = 1
player_health = 300

player_font = pg.font.Font('freesansbold.ttf', 30)
show_player_font = player_font.render('You', True, (255, 255, 255))

ammoImg = pg.image.load('fire-bullet.png')
ammo_state = 'ready'
ammoX = 0
ammoY = 480
ammoY_change = 0
ammoSpeed = 13

bullet_timer = 0
bullet_delay = 20

# Multiple Enemies
enemyImg = pg.image.load('enemy.png')
enemy_speed = 0.4  # Initial enemy speed

# Enemy Bullets
enemy_bullets = []  # List to hold enemy bullets
enemy_bullet_speed = 5
enemy_bullet_timer = 0
enemy_bullet_delay = 1500  # milliseconds between enemy bullets

# Create a list to store multiple enemies with unique IDs and health
initial_num_of_enemies = 16
enemies = []

# Boss
bossImg = pg.image.load('player5.png')
bossX = screen_mid_val[0] - 50  # Centered horizontally
bossY = screen_mid_val[1] - 250  # Set even higher from the middle of the screen
bossSpeed = 0.5  # Reduced speed for the boss
bossHealth = 150  # Boss health
boss_bullets = []  # List to hold boss's bullets
boss_bullet_speed = 7
boss_bullet_timer = 0
boss_bullet_delay = 2000  # milliseconds between each boss bullet

boss_font = pg.font.Font('freesansbold.ttf', 40)
font = pg.font.Font('freesansbold.ttf', 36)

boss_textX = 250
boss_textY = 250

boss_active = False

# Score
score_val = 0

textX = 10
textY = 20

# Abilities list
dropped_abilities = []

# Explosion
explosionImg = pg.image.load('explosion.png')

# Timer for explosions
explosions = []

#################### (Welcome Screen) ####################

def WelcomeScreen():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    # reset_game()  # Ensure game variables are reset
                    # MainGame()  # Start the game
                    return
                elif event.key == pg.K_q:
                    pg.quit()
                    sys.exit()

        screen.blit(pg.transform.scale(welcome_screen, (screen_width, screen_height)), (0, 0))
        screen.blit(show_welcome_font, (160, screen_height // 2 + 130))
        pg.display.update()
        FPSCLOCK.tick(FPS)

#################### (Main Game) ####################

def MainGame():
    global running, ammo_state, ammoY, ammoX, score_val, playerX, playerX_change, playerSpeed, player_health
    global bossX, bossY, bossHealth, boss_active, bullet_timer, bullet_delay, ammoY_change, boss_bullet_timer
    global enemy_speed

    screen.blit(pg.transform.scale(bg2, (800, 600)), (0, 0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                playerX_change = -playerSpeed
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                playerX_change = playerSpeed

        if event.type == pg.KEYUP:
            if (event.key == pg.K_LEFT or event.key == pg.K_a) or (event.key == pg.K_RIGHT or event.key == pg.K_d):
                playerX_change = 0

        if event.type == pg.USEREVENT + 1:
            deactivate_power_up('speed_boost')
        if event.type == pg.USEREVENT + 2:
            deactivate_power_up('rapid_fire')

    # Space key for continuous firing
    keys = pg.key.get_pressed()
    if keys[pg.K_SPACE]:
        current_time = pg.time.get_ticks()
        if ammo_state == 'ready' and current_time - bullet_timer > bullet_delay:
            bullet_timer = current_time
            ammoX = playerX
            ammoY = playerY
            shoot_bullet(ammoX, ammoY)
            ammoY_change = ammoSpeed
            gun_sound.play()

    playerX += playerX_change
    if playerX >= 736:
        playerX = 736
    if playerX <= 0:
        playerX = 0

    # Move and draw multiple enemies
    for enemy_data in enemies[:]:  # Iterate over a copy of the list to avoid modification issues
        enemy_data["x"] += enemy_data["x_change"]
        if enemy_data["x"] >= 736:
            enemy_data["x_change"] = -enemy_speed
            enemy_data["y"] += enemy_data["y_change"]
        elif enemy_data["x"] <= 0:
            enemy_data["x_change"] = enemy_speed
            enemy_data["y"] += enemy_data["y_change"]

        collision = isCollision(enemy_data["x"], enemy_data["y"], ammoX, ammoY, 27)
        if collision:
            enemy_data["health"] -= 13
            if enemy_data["health"] <= 0:
                score_val += 1
                add_explosion(enemy_data["x"], enemy_data["y"])
                explosion_sound.play()

                # Drop ability with a certain probability (e.g., 25% chance)
                if random.random() < 0.25:
                    dropped_abilities.append(drop_ability(enemy_data["x"], enemy_data["y"]))

                enemies.remove(enemy_data)
                ammoY = 480
                ammo_state = 'ready'
                add_enemy()  # Add a new enemy after removing one

        enemy(enemy_data["x"], enemy_data["y"], enemy_data["health"])

        move_enemy_bullets()
        for bullet in enemy_bullets:
            enemy_bullet(bullet[0], bullet[1])

    # Boss Activation
    if score_val >= 50:
        if not boss_active:
            boss_coming()
            boss_active = True
        if bossY < screen_mid_val[1] - 150:  # Move boss to a higher position
            bossY += bossSpeed
        else:
            bossY = screen_mid_val[1] - 150  # Final position is slightly higher from the middle
        Boss(bossX, bossY)

        current_time = pg.time.get_ticks()
        if current_time - boss_bullet_timer > boss_bullet_delay:
            boss_bullet_timer = current_time
            boss_bullets.append([bossX + 100, bossY + 150])  # Adjusted bullet position

        move_boss_bullets()

    if ammoY <= 0:
        ammoY = 480
        ammo_state = 'ready'

    if ammo_state == 'fire':
        shoot_bullet(ammoX, ammoY)
        ammoY -= ammoY_change

    # Boss Collision Detection and Health Reduction
    if boss_active:
        boss_collision = isPlayerBulletCollision(ammoX, ammoY, bossX, bossY, 40)
        if boss_collision:
            bossHealth -= 10  # Reduce boss health by 10 on each hit
            add_explosion(bossX, bossY)
            explosion_sound.play()
            if bossHealth <= 0:
                score_val += 10
                add_explosion(bossX, bossY)
                explosion_sound.play()
                boss_active = False
                bossHealth = 150  # Reset boss health for the next time
                bossX = screen_mid_val[0] - 50
                bossY = -100
            ammoY = 480
            ammo_state = 'ready'

    for bullet in boss_bullets[:]:
        if isBossBulletCollision(bullet[0], bullet[1], playerX, playerY):
            player_health -= 3
            boss_bullets.remove(bullet)
            if player_health <= 0:
                add_explosion(playerX, playerY)
                explosion_sound.play()
                GameOver()
                return
        elif bullet[1] > screen_height:
            boss_bullets.remove(bullet)

    for ability in dropped_abilities[:]:
        ability["y"] += 2  # Drop speed
        if ability["y"] > screen_height:
            dropped_abilities.remove(ability)
        else:
            draw_ability(ability)
            if (playerX < ability["x"] + 50 and playerX + 74 > ability["x"] and
                playerY < ability["y"] + 50 and playerY + 74 > ability["y"]):
                apply_ability(ability)
                dropped_abilities.remove(ability)
    

    player(playerX, playerY, player_health)
    show_score(textX, textY)
    show_explosions()
    show_power_up_timer()
    increase_difficulty()

    pg.display.update()

#################### (Player) ####################

def player(x, y, player_health):
    screen.blit(pg.transform.scale(playerImg, (74, 74)), (x, y))
    screen.blit(show_player_font, (420, 23))
    draw_health_bar_for_player(485, 20, player_health)

def shoot_bullet(x, y):
    global ammo_state
    ammo_state = 'fire'
    screen.blit(pg.transform.scale(pg.transform.rotate(ammoImg, 225), (80, 80)), (x, y + 10))

#################### (Enemy) ####################

def add_enemy():
    enemies.append({
        "x": random.randint(0, 736),
        "y": random.randint(50, 150),
        "x_change": enemy_speed,
        "y_change": 40,
        "id": uuid.uuid1(),
        "health": 100  # Initialize health for each enemy
    })

for _ in range(initial_num_of_enemies):
    add_enemy()

def enemy(x, y, health):
    screen.blit(enemyImg, (x, y))
    draw_health_bar(x, y, health)

def draw_health_bar(x, y, health):
    health_bar_width = 50
    health_bar_height = 5
    health_bar_x = x + 12
    health_bar_y = y - 10

    # Draw red background for health bar
    pg.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

    # Draw green foreground for health based on current health
    pg.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, max(health * (health_bar_width / 100), 0), health_bar_height))

def draw_health_bar_for_player(x, y, player_health):
    player_health_bar_width = 300
    player_health_bar_height = 30
    player_health_bar_x = x 
    player_health_bar_y = y

    # Draw red background for health bar
    pg.draw.rect(screen, (255, 0, 0), (player_health_bar_x, player_health_bar_y, player_health_bar_width, player_health_bar_height))

    # Draw green foreground for health based on current health
    pg.draw.rect(screen, (0, 255, 0), (player_health_bar_x, player_health_bar_y, max(player_health * (player_health_bar_width / 300), 0), player_health_bar_height))

# Function to make enemies fire bullets
def enemy_fire(enemy_data):
    global enemy_bullet_timer
    current_time = pg.time.get_ticks()
    if current_time - enemy_bullet_timer > enemy_bullet_delay:
        enemy_bullet_timer = current_time
        enemy_bullets.append([enemy_data["x"] + 37, enemy_data["y"] + 50])

# Move and draw enemy bullets
def move_enemy_bullets():
    global player_health
    for bullet in enemy_bullets[:]:
        bullet[1] += enemy_bullet_speed
        if bullet[1] > screen_height:
            enemy_bullets.remove(bullet)
        elif isEnemyBulletCollision(bullet[0], bullet[1], playerX, playerY):
            player_health -= 10  # Decrease player health when hit
            add_explosion(playerX, playerY)
            explosion_sound.play()
            enemy_bullets.remove(bullet)
            if player_health <= 0:
                GameOver()
                return

# Check if enemy bullet collides with player
def isEnemyBulletCollision(bulletX, bulletY, playerX, playerY):
    return (bulletX < playerX + 74 and bulletX + 10 > playerX and
            bulletY < playerY + 74 and bulletY + 20 > playerY)

# Function to draw enemy bullets
def enemy_bullet(x, y):
    pg.draw.rect(screen, (255, 255, 0), (x, y, 10, 20))

#################### (Boss) ####################

def display_text(text, duration):
    text_surface = font.render(text, True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=screen_mid_val)
    screen.blit(text_surface, text_rect)
    pg.display.update()
    pg.time.delay(duration)

displayed_text = False

def boss_coming():
    global displayed_text
    if not displayed_text:
        display_text('BOSS IS COMING', 2000)
        displayed_text = True

def Boss(x, y):
    screen.blit(pg.transform.scale(bossImg, (200, 200)), (x, y))
    # Draw health bar
    health_bar_width = 155
    health_bar_height = 10
    health_bar_x = x + 25
    health_bar_y = y - 25
    pg.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))  # Red background
    pg.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, max((bossHealth / 150) * health_bar_width, 0), health_bar_height))  # Green foreground

def boss_bullet(x, y):
    pg.draw.rect(screen, (255, 0, 0), (x + 40, y + 100, 10, 20))

def move_boss_bullets():
    for bullet in boss_bullets:
        bullet[1] += boss_bullet_speed
        boss_bullet(bullet[0], bullet[1])
        if bullet[1] > screen_height:
            if bullet in boss_bullets:
                boss_bullets.remove(bullet)

#################### (Collision) ####################

def isCollision(x1, y1, x2, y2, threshold):
    distance = math.sqrt((math.pow(x1 - x2, 2)) + (math.pow(y1 - y2, 2)))
    return distance < threshold

def isBossBulletCollision(boss_bullet_x, boss_bullet_y, playerX, playerY):
    if (boss_bullet_x < playerX + 74 and boss_bullet_x + 10 > playerX and
        boss_bullet_y < playerY + 74 and boss_bullet_y + 20 > playerY):
        return True
    return False

def isPlayerBulletCollision(amoX, ammoY, bossX, bossY, threshold):
    distance = math.sqrt((math.pow(amoX - (bossX + 100), 2)) + (math.pow(ammoY - (bossY + 100), 2)))
    return distance < threshold

# Showing Collision effect
def add_explosion(x, y):
    explosions.append({"x": x, "y": y, "start_time": pg.time.get_ticks()})

def show_explosions():
    current_time = pg.time.get_ticks()
    for explosion in explosions[:]:
        if current_time - explosion["start_time"] < 500:  # Display explosion for 500 ms
            screen.blit(pg.transform.scale(explosionImg, (80, 80)), (explosion["x"], explosion["y"]))
        else:
            explosions.remove(explosion)

#################### (Showing Score) ####################

def show_score(x, y):
    score = font.render("Score : " + str(score_val), True, (255, 255, 255))
    screen.blit(score, (x, y))

#################### (Ability drop and apply functionality) ####################

abilities = {
    "speed_boost": {
        "image": pg.image.load('speed-bost.png'),
        "duration": 10000  # Duration in milliseconds
    },
    "rapid_fire": {
        "image": pg.image.load('fire-bullet.png'),
        "duration": 10000  # Duration in milliseconds
    }
}

active_power_ups = {}

def drop_ability(x, y):
    ability_type = random.choice(list(abilities.keys()))
    ability = abilities[ability_type]
    return {
        "type": ability_type,
        "x": x,
        "y": y,
        "image": ability["image"]
    }

def draw_ability(ability):
    screen.blit(pg.transform.scale(ability["image"], (50, 50)), (ability["x"], ability["y"]))

def apply_ability(ability):
    global playerSpeed, ammoSpeed
    if ability["type"] == "speed_boost":
        playerSpeed *= 1.5
        active_power_ups["speed_boost"] = pg.time.get_ticks() + abilities["speed_boost"]["duration"]
    elif ability["type"] == "rapid_fire":
        # ammoSpeed = 12
        active_power_ups["rapid_fire"] = pg.time.get_ticks() + abilities["rapid_fire"]["duration"]

def show_power_up_timer():
    current_time = pg.time.get_ticks()
    for power_up, end_time in active_power_ups.items():
        remaining_time = max((end_time - current_time) // 1000, 0)
        timer_font = pg.font.Font('freesansbold.ttf', 24)
        timer_text = timer_font.render(f"{power_up.replace('_', ' ').title()}: {remaining_time}s", True, (255, 255, 0))
        if power_up == "speed_boost":
            screen.blit(timer_text, (10, 60))
        elif power_up == "rapid_fire":
            screen.blit(timer_text, (10, 90))

def deactivate_power_up(power_up_type):
    global playerSpeed, bullet_delay
    if power_up_type in active_power_ups:
        if power_up_type == "speed_boost":
            playerSpeed /= 1.5
        elif power_up_type == "rapid_fire":
            bullet_delay = 20
        del active_power_ups[power_up_type]

#################### (Game Over) ####################

def GameOver():
    game_over_font = pg.font.SysFont('Corbel', 64)
    show_game_over_font = game_over_font.render('GAME OVER', True, (255, 0, 0))
    screen.blit(show_game_over_font, (200, 250))
    pg.display.update()
    pg.time.delay(2000)  # Pause for 2 seconds before showing the restart option

    restart_game()

def restart_game():
    # Show restart or quit options
    restart_font = pg.font.Font('freesansbold.ttf', 32)
    restart_text = restart_font.render("Press 'R' to Restart or 'Q' to Quit", True, (255, 255, 255))
    screen.blit(restart_text, (150, 350))
    pg.display.update()

    # Wait for user input to restart or quit
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    MainGame()
                elif event.key == pg.K_q:
                    pg.quit()
                    quit()

def reset_game():
    global playerX, playerY, player_health, ammo_state, ammoY, ammoX, score_val, bossX, bossY, bossHealth
    global boss_active, enemies, boss_bullets, bullet_timer, dropped_abilities

    # Reset player attributes
    playerX = 370
    playerY = 480
    player_health = 300  # Reset player health to full
    ammo_state = 'ready'
    ammoY = 480
    ammoX = 0

    # Reset score and other attributes
    score_val = 0
    bossX = screen_mid_val[0] - 50
    bossY = screen_mid_val[1] - 250
    bossHealth = 150
    boss_active = False
    boss_bullets = []
    
    # Reset enemies and power-ups
    enemies.clear()
    for _ in range(initial_num_of_enemies):
        add_enemy()
    
    dropped_abilities.clear()

    bullet_timer = 0

#################### (Difficulty Increase Over Time) ####################

def increase_difficulty():
    global enemy_speed, boss_bullet_delay
    # Increase enemy speed based on score
    if score_val >= 50:
        enemy_speed = 0.6
    if score_val >= 100:
        enemy_speed = 0.8
    if score_val >= 150:
        enemy_speed = 1.0

    # Optionally, decrease boss bullet delay to increase difficulty
    if score_val >= 50:
        boss_bullet_delay = max(500, boss_bullet_delay - (score_val // 10) * 100)

#################### (Initializing Pygame) ####################

if __name__ == "__main__":
    pg.init()
    FPSCLOCK = pg.time.Clock()

    screen = pg.display.set_mode((screen_width, screen_height))
    pg.display.set_caption("Space Invader Game by Ashish")
    icon = pg.image.load('space-icon.png')
    pg.display.set_icon(icon)

    # Background music
    mixer.music.load('pathan-song.mp3')
    mixer.music.play(-1)

    # Gunfiring sound
    gun_sound = mixer.Sound('fire-sound.wav')

    # Explosion sound
    explosion_sound = mixer.Sound('Blast.wav')

while running:
    # WelcomeScreen()
    MainGame()
    # GameOver()
    # running = False  # Exit after game over

pg.quit()
