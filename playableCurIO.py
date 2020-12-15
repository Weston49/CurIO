import sys
import neat
import pygame
import random
import tkinter as tk
toggle = False
def stopp():
    root.destroy()
    sys.exit()
    
def start():
    global startGame
    startGame = True
    pygame.init()
    root.destroy()
    if toggle:  
        main()
def menu():
    global root
    root = tk.Tk()
    root.title("CurI/O")
    frame = tk.Frame(root)
    frame.pack()
    bg = tk.PhotoImage(file="menuBg.png")
    bgImg = tk.Label(frame, image=bg)
    bgImg.pack()
    button = tk.Button(frame, 
                    text="Quit", 
                    fg="red",
                    font=("Courier", 34),
                    command=stopp)
    button.place(x = 150, y = 125, width=200, height=50)
    button2 = tk.Button(frame, 
                    text="Start", 
                    fg="green",
                    font=("Courier", 34),
                    command=start)
    button2.place(x = 150, y = 50, width=200, height=50)
    root.mainloop()
menu()
pygame.init()
win_width = 1244
win_height = 800
slime_imgBIG = pygame.image.load("SLIME.png")
slime_img = pygame.transform.scale(slime_imgBIG,(128,128))
bg_img = pygame.image.load("bg.png")
floor_img = pygame.transform.scale(pygame.image.load("floor.png"),(256,72))
rock_img = pygame.image.load("rock.png")
font = pygame.font.SysFont("comicsans", 90)



class Rock:
    def __init__(self,x,y,velX,velY):
        self.x = x
        self.y = y
        self.velX = velX
        self.velY = velY
        self.img = rock_img
    def move(self):
        self.x += self.velX
        self.y += self.velY
    def collide(self,ball):
        ball_mask = ball.get_mask()
        rock_mask = pygame.mask.from_surface(self.img)
        offset = (round((self.x - ball.x)+ball.vel), round((self.y - ball.y)+ball.jump_vel+2))
        point = ball_mask.overlap(rock_mask, offset)
        if point:
            return True
        else:
            return False
    def draw(self,win):
        win.blit(self.img, (self.x,self.y))
class Bg:
    WIDTH = bg_img.get_width()
    IMG = bg_img
    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    def move(self):
        self.x1 -= 2
        self.x2 -= 2

        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

            
    def draw(self,win):
        win.blit(self.IMG,(round(self.x1),self.y))
        win.blit(self.IMG,(round(self.x2),self.y))

class Floor:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.img = floor_img
    def move(self):
        self.x -= 10
    def draw(self,win):
        win.blit(self.img,(self.x,self.y))
    def collide(self,ball):
        ball_mask = ball.get_mask()
        floor_mask = pygame.mask.from_surface(self.img)
        offset = (round((self.x - ball.x)+ball.vel), round(self.y - ball.y))
        point = ball_mask.overlap(floor_mask, offset)
        if point:
            return True
        else:
            return False
class Ball:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.jump_vel = 0
        self.img = slime_img
        self.jump_time = 0
        self.jumping = False
        self.onGround = False
        self.dropTimer = 0
        self.animation_timer = 0
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    def fall(self):
        if self.jump_vel > -20:
            self.jump_vel -= 2
        else:
            self.jump_vel = -20
    def jump(self):
        if self.jumping == False:
            if self.onGround == True:
                self.jump_vel = 24
                self.onGround = False
            self.jump_time += 1
            if self.jump_time > 4:
                self.fall()
            else:
                if self.jump_vel < 28:
                    self.jump_vel += 1.5
                else:
                    self.jump_vel = 28
        else:
            self.fall()
            
    def move_right(self):
        if self.vel >= 12:
            self.vel = 12
        else:
            self.vel += 2
    def move_left(self):
        if self.vel <= -12:
            self.vel = -12
        else:
            self.vel -= 2
    def slow(self):
        if self.vel == 0:
            self.vel = 0
        elif self.vel < 0:
            self.vel += 2
        elif self.vel > 0:
            self.vel -= 2
    def draw(self,win):
        self.x += self.vel
        self.tilt += (self.vel*-1)*1.8
        self.y -= self.jump_vel
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (round(self.x), round(self.y))).center)
        win.blit(rotated_image,new_rect.topleft)
def draw_window(win,game_speed,bg,score,balls,floors,rocks):
    bg.draw(win)
    #scoreTxt = font.render(("Score: "+str(score)), 1, (255,255,255))
    #win.blit(scoreTxt, ((win_width-scoreTxt.get_width()),20))
    for floor in floors:
        floor.draw(win)
        floor.move()
    for ball in balls:
        ball.draw(win)
    for rock in rocks:
        rock.draw(win)
    pygame.display.update()
def main():
    global toggle
    toggle = True
    died = False
    win = pygame.display.set_mode((win_width,win_height))
    random.seed(420)
    score = 0
    bg = Bg(0)
    balls = []
    floors = []
    rocks = []
    game_speed = 25
    play = True
    clock = pygame.time.Clock()
    player = Ball(900,-1800)
    floor = Floor(1500,775)
    rock = Rock(0,0,5,5)
    rocks.append(rock)
    floors.append(floor)
    balls.append(player)
    floor_clock = 120
    rock_clock = -10
    score_clock = 0
    while play:
        
        clock.tick(game_speed)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
                pygame.quit()
                quit()
        # Adding the scores 
        if score_clock <= 5:
            score_clock += 1
        else:
            score_clock = 0
            score += 1
        #Creating the floors
        r = random.randrange(5,120)
        if floor_clock < r:
            floor_clock += 1
        else:
            picker = random.randrange(0,100)
            if picker < 33 or picker > 66:
                floor = Floor(1500,775)
                floors.append(floor)
            if picker > 25 and picker < 60:
                floor = Floor(1500,475)
                floors.append(floor)
            if picker > 40 and picker < 75:
                floor = Floor(1500,175)
                floors.append(floor)
            if picker == 33 or picker == 66 or picker == 25 or picker == 60 or picker == 40 or picker == 75:
                pass

            floor_clock = 0
        #removing the floors 
        for floor in floors:
            if floor.x < -500:
                floors.remove(floor)
        #creating the rocks
        for rock in rocks:
            if rock.y > 850:
                rocks.remove(rock)
                x = random.randrange(-10,1244)
                y = random.randrange(-100,-50)
                if x > 622:
                    velX = random.randrange(-8,-1)
                    velY = random.randrange(4,6)
                else:
                    velX = random.randrange(1,8)
                    velY = random.randrange(4,6)
                rock = Rock(x,y,velX,velY)
                rocks.append(rock)
        #Moving the balls
        for x, ball in enumerate(balls):
            if ball.y < 0:
                ball.y = 0
                ball.jump_vel = -1
            if ball.x < 0:
                ball.x = 0
                ball.vel = 0
            if ball.x > 1130:
                ball.x = 1130
                ball.vel = 0
            for floor in floors:
                if floor.collide(ball):
                    if ball.jump_vel < -15 or ball.jump_vel == 0:
                        ball.jump_vel = 0
                        ball.onGround = True
                        ball.jumping = False
                        ball.dropTimer = 25
                else:
                    ball.dropTimer -= 1
                    if ball.dropTimer < 0:
                        ball.onGround = False
            for rock in rocks:
                if rock.collide(ball):
                    balls.pop(x)
                    died = True
            if ball.y > win_height + 75:
                balls.pop(x)
                died = True
        for rock in rocks:
            rock.move()
        #Checking for keys, inputs
        keys = pygame.key.get_pressed()
        for ball in balls:
            if keys[pygame.K_RIGHT]:
                ball.move_right()
            if keys[pygame.K_LEFT]:
                ball.move_left()
            if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                ball.slow()
            if keys[pygame.K_UP]:
                ball.jump()
            if not keys[pygame.K_UP]:
                if ball.onGround == False:   
                    ball.fall()
                    ball.jumping = True
                else:
                    pass
                ball.jump_time = 0
            
        bg.move()
                
        draw_window(win,clock,bg,score,balls,floors,rocks)
        if died:
            pygame.quit()
            menu()
if startGame:
    main()

