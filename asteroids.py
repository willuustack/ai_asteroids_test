import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the game window (very large map)
screen_width, screen_height = 5000, 4000  # Significantly larger playing area
screen = pygame.display.set_mode((1200, 900))  # Viewport size
pygame.display.set_caption('Asteroids AI')

# Set up the font for the score counter
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

# Set up the clock to regulate the game loop
clock = pygame.time.Clock()
FPS = 60  # Set the frames per second (TPS)

# Spaceship class
class Spaceship:
    def __init__(self, x, y):
        self.original_image = pygame.Surface((20, 20), pygame.SRCALPHA)  # Smaller spaceship with alpha transparency
        pygame.draw.polygon(self.original_image, (255, 255, 255), [(10, 0), (0, 20), (20, 20)])  # Draw a triangle
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rotation_speed = 3  #Rotation speed
        self.acceleration = 0.6  #Acceleration for movement
        self.max_speed = 5  #Max speed
        self.friction = 0.99  # Friction to control speed

    def rotate(self, direction):
        if direction == "left":
            self.angle -= self.rotation_speed
        elif direction == "right":
            self.angle += self.rotation_speed

        # Rotate the image and update the rect
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def accelerate(self):
        # Accelerate in the direction the spaceship is facing
        radians = math.radians(self.angle)
        self.speed_x += self.acceleration * math.sin(radians)
        self.speed_y -= self.acceleration * math.cos(radians)

        # Clamp speed to max speed
        speed = math.sqrt(self.speed_x ** 2 + self.speed_y ** 2)
        if speed > self.max_speed:
            self.speed_x = self.max_speed * self.speed_x / speed
            self.speed_y = self.max_speed * self.speed_y / speed

    def update(self):
        # Apply friction
        self.speed_x *= self.friction
        self.speed_y *= self.friction

        # Update position based on speed
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wrap around map boundaries
        if self.rect.left > screen_width:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = screen_width
        if self.rect.top > screen_height:
            self.rect.bottom = 0
        elif self.rect.bottom < 0:
            self.rect.top = screen_height

    def draw(self, screen, offset_x, offset_y):
        # Draw the spaceship adjusted by the viewport offset
        screen.blit(self.image, (self.rect.topleft[0] - offset_x, self.rect.topleft[1] - offset_y))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

# Asteroid class
class Asteroid:
    def __init__(self, x, y, tier=3):
        self.tier = tier
        size = {3: 200, 2: 80, 1: 50}[tier]  # Sizes for different tiers
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = random.uniform(-1, 1) * (4 - tier)  # Larger asteroids move slower
        self.speed_y = random.uniform(-1, 1) * (4 - tier)
        self.points = self.create_points(size)
        pygame.draw.polygon(self.image, (128, 128, 128), self.points)

    def create_points(self, size):
        points = []
        for i in range(8):  # 8 vertices for uneven shape
            angle = i * math.pi / 4  # 45 degrees between each point
            radius = random.randint(size // 2 - 10, size // 2)
            x = size // 2 + radius * math.cos(angle)
            y = size // 2 + radius * math.sin(angle)
            points.append((x, y))
        return points

    def update(self):
        # Update position based on speed
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wrap around map boundaries
        if self.rect.left > screen_width:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = screen_width
        if self.rect.top > screen_height:
            self.rect.bottom = 0
        elif self.rect.bottom < 0:
            self.rect.top = screen_height

    def draw(self, screen, offset_x, offset_y):
        # Draw the asteroid adjusted by the viewport offset
        screen.blit(self.image, (self.rect.topleft[0] - offset_x, self.rect.topleft[1] - offset_y))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

    def break_apart(self):
        # Break into smaller asteroids if not the smallest tier
        if self.tier > 1:
            num_new_asteroids = 3 if self.tier == 2 else 2
            new_tier = self.tier - 1
            return [Asteroid(self.rect.centerx, self.rect.centery, new_tier) for _ in range(num_new_asteroids)]
        return []

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.image = pygame.Surface((5, 5), pygame.SRCALPHA)  # Small bullet
        pygame.draw.circle(self.image, (255, 255, 0), (2, 2), 2)  # Yellow bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 10  # Speed of the bullet

    def update(self):
        radians = math.radians(self.angle)
        self.rect.x += self.speed * math.sin(radians)
        self.rect.y -= self.speed * math.cos(radians)

    def draw(self, screen, offset_x, offset_y):
        # Draw the bullet adjusted by the viewport offset
        screen.blit(self.image, (self.rect.topleft[0] - offset_x, self.rect.topleft[1] - offset_y))

    def off_screen(self):
        # Check if the bullet is off-screen
        return (self.rect.right < 0 or self.rect.left > screen_width or
                self.rect.bottom < 0 or self.rect.top > screen_height)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

# Function to draw a dark background with a white grid
def draw_background(screen, grid_size=50):
    screen.fill((10, 10, 10))  # Dark background color
    for x in range(0, screen_width, grid_size):
        pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, screen_height))
    for y in range(0, screen_height, grid_size):
        pygame.draw.line(screen, (255, 255, 255), (0, y), (screen_width, y))

# Function to display a countdown before respawn
def display_countdown(screen, countdown):
    countdown_text = font.render(f"Respawning in {countdown}...", True, (255, 255, 255))
    screen.blit(countdown_text, (screen.get_width() // 2 - countdown_text.get_width() // 2, screen.get_height() // 2))

# Function to display Game Over
def display_game_over(screen):
    game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
    screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, screen.get_height() // 2))

# Create the spaceship instance
spaceship = Spaceship(screen_width // 2, screen_height // 2)

# Create a few asteroids
asteroids = [Asteroid(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(40)]

# Initialize bullet list
bullets = []

# Initialize the score
score = 0

# Initialize player lives
lives = 3

# Bullet cooldown timer
last_shot_time = 0
cooldown_time = 500  # Milliseconds between shots

# Respawn timer
respawn_time = 3000  # 3 seconds
respawning = False
respawn_start_time = 0

# Main game loop
running = True
while running:
    # Regulate the game loop speed
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not respawning:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            spaceship.rotate("left")
        if keys[pygame.K_RIGHT]:
            spaceship.rotate("right")
        if keys[pygame.K_UP]:
            spaceship.accelerate()
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time > cooldown_time:
                # Shoot a bullet out of the front of the spaceship
                bullet = Bullet(spaceship.rect.centerx, spaceship.rect.centery, spaceship.angle)
                bullets.append(bullet)
                last_shot_time = current_time

        # Update spaceship position
        spaceship.update()

    # Update bullet positions
    for bullet in bullets:
        bullet.update()

    # Remove bullets that are off-screen
    bullets = [bullet for bullet in bullets if not bullet.off_screen()]

    # Update asteroid positions
    for asteroid in asteroids:
        asteroid.update()

    # Calculate the viewport offset so the spaceship is centered
    offset_x = spaceship.rect.centerx - screen.get_width() // 2
    offset_y = spaceship.rect.centery - screen.get_height() // 2

    # Draw the background grid
    draw_background(screen)

    # Draw the spaceship, asteroids, and bullets with offset
    if not respawning:
        spaceship.draw(screen, offset_x, offset_y)
    for asteroid in asteroids:
        asteroid.draw(screen, offset_x, offset_y)
    for bullet in bullets:
        bullet.draw(screen, offset_x, offset_y)

    if not respawning:
        # Check for collisions using masks for pixel-perfect detection
        spaceship_mask = spaceship.get_mask()

        for asteroid in asteroids[:]:
            asteroid_mask = asteroid.get_mask()
            offset = (asteroid.rect.left - spaceship.rect.left, asteroid.rect.top - spaceship.rect.top)
            collision_point = spaceship_mask.overlap(asteroid_mask, offset)

            if collision_point:
                print("Collision detected at:", collision_point)
                lives -= 1  # Decrease lives on collision
                if lives > 0:
                    respawning = True
                    respawn_start_time = pygame.time.get_ticks()
                else:
                    running = False  # End the game if no lives are left

            # Check for bullet-asteroid collisions
            for bullet in bullets[:]:
                bullet_mask = bullet.get_mask()
                bullet_offset = (asteroid.rect.left - bullet.rect.left, asteroid.rect.top - bullet.rect.top)
                bullet_collision = bullet_mask.overlap(asteroid_mask, bullet_offset)

                if bullet_collision:
                    print("Bullet hit an asteroid!")
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    new_asteroids = asteroid.break_apart()
                    asteroids.extend(new_asteroids)
                    if asteroid.tier == 1:
                        score += 1  # Increase score when a tier 1 asteroid is destroyed
                    break

    # Respawn logic
    if respawning:
        current_time = pygame.time.get_ticks()
        countdown = 3 - (current_time - respawn_start_time) // 1000
        display_countdown(screen, countdown)
        if current_time - respawn_start_time >= respawn_time:
            respawning = False
            spaceship = Spaceship(screen_width // 2, screen_height // 2)

    # Draw the score counter and lives
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))

    # Update the display
    pygame.display.flip()

# Game over screen
display_game_over(screen)
pygame.display.flip()
pygame.time.wait(3000)  # Display Game Over for 3 seconds before quitting

pygame.quit()
sys.exit()