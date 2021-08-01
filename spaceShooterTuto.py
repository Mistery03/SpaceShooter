import pygame;
import os;
import time;
import random;
import sys;

pygame.font.init();

WIDTH, HEIGHT = 700, 500;
WIN = pygame.display.set_mode((WIDTH,HEIGHT));
pygame.display.set_caption("Space Shooter Tutorial");

#Load images

#Enemies' ship
REDSPACESHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"));
GREENSPACESHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"));
BLUESPACESHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"));

#Player's ships
YELLOWSPACESHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"));

#Lasers
REDLASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"));
GREENLASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"));
BLUELASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"));
YELLOWLASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"));

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT));

class Laser:
    def __init__(self,x ,y, img):
        self.x = x;
        self.y = y;
        self.img = img;
        self.mask = pygame.mask.from_surface(self.img);

    def draw(self,window):
        window.blit(self.img, (self.x,self.y));

    def move(self,vel):
        self.y += vel;

    def offScreen(self,height):
        return not(self.y <= height and self.y >= 0);

    def collision(self,obj):
        return collide(obj,self);
        
class Ship:
    COOLDOWN = 30;
    
    def __init__(self, x, y, health = 100):
        self.x = x;
        self.y = y;
        self.health = health;
        self.shipImg = None;
        self.laserImg = None;
        self.lasers = [];
        self.coolDownCounter = 0;

    def draw(self, window):
        window.blit(self.shipImg, (self.x, self.y));
        for laser in self.lasers:
            laser.draw(window);

    def moveLasers(self,vel,obj):
        self.cooldown();
        for laser in self.lasers:
            laser.move(vel);
            if laser.offScreen(HEIGHT):
                self.lasers.remove(laser);
            elif laser.collision(obj):
                obj.health -= 10;
                self.lasers.remove(laser);
                
    def cooldown(self):
        if self.coolDownCounter >= self.COOLDOWN:
            self.coolDownCounter =0;
        elif self.coolDownCounter > 0:
            self.coolDownCounter += 1;
            
    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x,self.y, self.laserImg);
            self.lasers.append(laser);
            self.coolDownCounter = 1;
            
    def getWidth(self):
        return self.shipImg.get_width();

    def getHeight(self):
        return self.shipImg.get_height();

class Player(Ship):
    def __init__(self,x,y,health = 100):
        super().__init__(x,y,health);
        self.shipImg = YELLOWSPACESHIP;
        self.laserImg = YELLOWLASER;
        self.mask = pygame.mask.from_surface(self.shipImg);
        self.maxHealth = health;

    def moveLasers(self,vel,objs):
        self.cooldown();
        for laser in self.lasers:
            laser.move(vel);
            if laser.offScreen(HEIGHT):
                self.lasers.remove(laser);
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj);
                        self.lasers.remove(laser);

    def draw(self,window):
        super().draw(window);
        self.healthbar(window);

    def healthbar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.shipImg.get_height()+ 10, self.shipImg.get_width(), 10));
        pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.shipImg.get_height()+ 10, self.shipImg.get_width() * (self.health/self.maxHealth), 10));

class Enemy(Ship):
    COLORMAP = {
        "red": (REDSPACESHIP,REDLASER),
        "green":(GREENSPACESHIP,GREENLASER),
        "blue":(BLUESPACESHIP,BLUELASER)
        };
    
    def __init__(self,x,y,color, health = 100):
        super().__init__(x,y,health);
        self.shipImg, self.laserImg = self.COLORMAP[color];
        self.mask = pygame.mask.from_surface(self.shipImg);

    def move(self,vel):
        self.y += vel;

    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x-20, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDownCounter = 1 

def collide(obj1, obj2):
    offsetX = obj2.x - obj1.x;
    offsetY = obj2.y - obj1.y;
    return obj1.mask.overlap(obj2.mask,(offsetX,offsetY)) != None;

def main():
    run = True;
    FPS = 60;
    level = 0;
    lives = 3;
    lost = False;
    lostCount = 0;
    mainFont = pygame.font.SysFont("Verdana",50);
    lostFont = pygame.font.SysFont("Verdana",60);

    enemies = [];
    waveLength = 5;
    enemyVel = 1;

    playerVel = 5;

    laserVel = 4;

    player = Player(300,380);
    
    clock = pygame.time.Clock();

    def redrawWindow():
        WIN.blit(BG,(0,0));
        #Draw text
        livesLabel = mainFont.render(f"Lives: {lives}", 1,(255,0,0));
        levelLabel = mainFont.render(f"Level: {level}",1,(255,255,255));

        WIN.blit(livesLabel, (10,10));
        WIN.blit(levelLabel,(WIDTH - levelLabel.get_width() - 10,10));

        for enemy in enemies:
            enemy.draw(WIN);

        player.draw(WIN);

        if lost:
            lostLabel = lostFont.render("You died", 1 ,(255,0,0));
            WIN.blit(lostLabel, (WIDTH/2 - lostLabel.get_width()/2, 250));
            
        
        pygame.display.update();

    while run:
        clock.tick(FPS);

        redrawWindow();
        

        if lives <= 0 or player.health <= 0:
            lost = True;
            lostCount += 1;

        if lost:
            if lostCount > FPS * 3:
                run = False;
            else:
                continue;

        if len(enemies) == 0:
            level += 1;
            waveLength += 5;
            for i in range(waveLength):
                enemy = Enemy(random.randrange(50,WIDTH - 100), random.randrange(-1500*level/2, -100), random.choice(["red","blue","green"]));
                enemies.append(enemy);

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                exit();
                
        keys = pygame.key.get_pressed();
        if keys[pygame.K_a] and player.x - playerVel > 0: #left
            player.x -= playerVel;
        if keys[pygame.K_d] and player.x + playerVel + player.getWidth() < WIDTH: #right
            player.x += playerVel;
        if keys[pygame.K_w] and player.y - playerVel > 0: #up
            player.y -= playerVel;
        if keys[pygame.K_s] and player.y + playerVel + player.getHeight() + 15 < HEIGHT: #down
            player.y += playerVel;
        if keys[pygame.K_SPACE]:
            player.shoot();

        for enemy in enemies[:]:
            enemy.move(enemyVel);
            enemy.moveLasers(laserVel,player);

            if random.randrange(0,2*60) == 1:
                enemy.shoot();

            if collide(enemy,player):
                player.health -= 10;
                enemies.remove(enemy);
            elif enemy.y + enemy.getHeight() > HEIGHT:
                lives -= 1;
                enemies.remove(enemy);

        player.moveLasers(-laserVel, enemies);

def mainMenu():
    titleFont = pygame.font.SysFont("Verdana",45);
    run = True;
    while run:
        WIN.blit(BG,(0,0));
        titleLabel = titleFont.render("Press the mouse to begin...",1,(255,255,255));
        WIN.blit(titleLabel,(WIDTH/2 - titleLabel.get_width()/2,350));

        pygame.display.update();
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False;
            if event.type == pygame.MOUSEBUTTONDOWN:
                main();
                
if __name__ == "__main__":
     mainMenu();
            
        
