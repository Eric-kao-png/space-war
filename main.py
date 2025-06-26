import random
import os
import pygame

FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WIDTH = 500
HEIGHT = 600

# init
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space War")
clock = pygame.time.Clock()

# font
font_name = pygame.font.match_font("arial")


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)


# load images
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19)).convert()
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
explosion_animations = {}
explosion_animations['large'] = []
explosion_animations['small'] = []
explosion_animations['player'] = []
for i in range(9):
    explosion_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    explosion_img.set_colorkey(BLACK)
    explosion_animations['large'].append(pygame.transform.scale(explosion_img, (75, 75)))
    explosion_animations['small'].append(pygame.transform.scale(explosion_img, (30, 30)))
for i in range(9):
    player_explosion_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_explosion_img.set_colorkey(BLACK)
    explosion_animations['player'].append(player_explosion_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs['shield'].set_colorkey(BLACK)
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()
power_imgs['gun'].set_colorkey(BLACK)

# load sounds
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
death_explosion_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
explosion_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav")),
]
power_sounds = {}
power_sounds['shield'] = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
power_sounds['gun'] = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))

pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.5)


# objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun_level = 0
        self.gun_up_time = 0

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            
        if self.gun_level > 0 and pygame.time.get_ticks() - self.gun_up_time > 5000:
            self.gun_level -= 1
            self.gun_up_time = pygame.time.get_ticks()
            
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speed_x
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        if not (self.hidden):   
            if self.gun_level == 0:
                bullet = Bullet(self.rect.centerx, self.rect.top, 0)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun_level == 1:
                bullet_a = Bullet(self.rect.centerx - 25, self.rect.top, 0)
                bullet_b = Bullet(self.rect.centerx + 25, self.rect.top, 0)
                all_sprites.add(bullet_a)
                all_sprites.add(bullet_b)
                bullets.add(bullet_a)
                bullets.add(bullet_b)
                shoot_sound.play()
            elif self.gun_level == 2:
                bullet_a = Bullet(self.rect.centerx - 25, self.rect.top, -2)
                bullet_b = Bullet(self.rect.centerx, self.rect.top, 0)
                bullet_c = Bullet(self.rect.centerx + 25, self.rect.top, 2)
                all_sprites.add(bullet_a)
                all_sprites.add(bullet_b)
                all_sprites.add(bullet_c)
                bullets.add(bullet_a)
                bullets.add(bullet_b)
                bullets.add(bullet_c)
                shoot_sound.play()
            elif self.gun_level == 3:
                bullet_a = Bullet(self.rect.centerx - 25, self.rect.top, random.randrange(-1, 3))
                bullet_b = Bullet(self.rect.centerx, self.rect.top, random.randrange(-2, 2))
                bullet_c = Bullet(self.rect.centerx + 25, self.rect.top, random.randrange(-3, 1))
                all_sprites.add(bullet_a)
                all_sprites.add(bullet_b)
                all_sprites.add(bullet_c)
                bullets.add(bullet_a)
                bullets.add(bullet_b)
                bullets.add(bullet_c)
                shoot_sound.play()
        
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 500)
        
    def gun_up(self):
        if self.gun_level < 3:
            self.gun_level += 1
        self.gun_up_time = pygame.time.get_ticks()


def draw_health(surf, health, x, y):
    if health < 0:
        health = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (health / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surt, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32 * i
        img_rect.y = y
        surt.blit(img, img_rect)


def draw_init(surf):
    screen.blit(background_img, (0, 0))
    draw_text(surf, "Space War", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(surf, "A and D for control the ship, space for shooting", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(surf, "press any key to start", 22, WIDTH / 2, HEIGHT / 2 + 22)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(rock_imgs)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2 * 0.85
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        self.speed_x = random.randrange(-3, 3)
        self.speed_y = random.randrange(2, 10)
        self.total_rotate_degree = 0
        self.per_rotate_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_rotate_degree += self.per_rotate_degree
        self.total_rotate_degree %= 360
        self.image = pygame.transform.rotate(
            self.image_original, self.total_rotate_degree
        )
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_x = random.randrange(-3, 3)
            self.speed_y = random.randrange(2, 10)


def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10
        self.speed_x = speed_x

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animations[size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animations[self.size]):
                self.kill()
            else:
                self.image = explosion_animations[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed_y = 3
        
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()


# game init
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group() 
player = Player()
all_sprites.add(player)
rocks = pygame.sprite.Group()
for i in range(8):
    new_rock()
score = 0
pygame.mixer.music.play(-1)

# game loop
show_init = True
running = True
while running:
    if show_init:
        closed = draw_init(screen)
        if closed:
            break
        show_init = False
        
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group() 
        player = Player()
        all_sprites.add(player)
        rocks = pygame.sprite.Group()
        for i in range(8):
            new_rock()
        score = 0
        pygame.mixer.music.play(-1)
        
    
    clock.tick(FPS)
    # input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # update
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        score += int(hit.radius)
        new_rock()
        random.choice(explosion_sounds).play()
        explosion = Explosion(hit.rect.center, 'large')
        all_sprites.add(explosion)
        if random.random() < 0.1:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powers.add(power)

    hits = pygame.sprite.spritecollide(
        player, rocks, True, pygame.sprite.collide_circle
    )
    for hit in hits:
        new_rock()
        random.choice(explosion_sounds).play()
        explosion = Explosion(hit.rect.center, 'small')
        all_sprites.add(explosion)
        player.health -= int(hit.radius)
        if player.health <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            death_explosion_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        type = hit.type
        if type == 'shield':
            player.health += 20
            power_sounds['shield'].play()
            if player.health > 100:
                player.health = 100
        if type == 'gun':
            player.gun_up()
            power_sounds['gun'].play()
        
    
    if player.lives <= 0 and not (death_explosion.alive()):
        show_init = True

    # render

    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_health(screen, player.health, 5, 18)
    draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 19)
    pygame.display.update()
