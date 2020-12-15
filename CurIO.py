import sys
import math
import neat
import pygame
import random
import os
import time
import re
import tkinter as tk
startGame = False
seed = 123456
def stopp():
    root.destroy()
    sys.exit()
    
def start():
    global startGame
    startGame = True
    root.destroy()
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
    def get_seed():
        global seed
        seed = int(entry.get())
        print("Seed:" + str(seed))
        entry.config(bg = "lime")
    def change_color():
        entry.config(bg = "white")
    button3 = tk.Button(frame, 
                    text="Confirm Seed", 
                    fg="black",
                    command=get_seed)
    button3.place(x = 300, y = 600, width=90, height=35)
    entry = tk.Entry(frame,
                     bg="white")

    entry.place(x = 130, y = 600, width=170, height = 35)
    entry.insert(0,"123456")

    root.mainloop()
menu()
pygame.init()
print(seed)
win_width = 1244
win_height = 800
slime_imgBIG = pygame.image.load("SLIME.png")
slime_img = pygame.transform.scale(slime_imgBIG,(128,128))
bg_img = pygame.image.load("bg.png")
floor_img = pygame.transform.scale(pygame.image.load("floor.png"),(256,72))
rock_img = pygame.transform.scale(pygame.image.load("rock.png"),(64,64))
font = pygame.font.SysFont("comicsans", 90)

class Line:
    def __init__(self,x1,y1,x2,y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.color = (0,0,0)
    def draw(self,win):
        pygame.draw.line(win,self.color,(self.x1,self.y1),(self.x2,self.y2))
class Circ:
    def __init__(self,x,y,color,radius,index):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.index = index
    def draw(self,win):
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius)
  
class Rock:
    def __init__(self,x,y,velX,velY):
        self.x = x
        self.y = y
        self.velX = velX
        self.velY = velY
        self.img = rock_img
        self.tilt = 0
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
        self.tilt += (self.velX*-1)
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (round(self.x), round(self.y))).center)
        win.blit(rotated_image,new_rect.topleft)

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
        if ball.jump_vel < -15 or ball.jump_vel == 0:
            ball_mask = ball.get_mask()
            floor_mask = pygame.mask.from_surface(self.img)
            offset = (round((self.x - ball.x)+ball.vel), round(self.y - ball.y))
            point = ball_mask.overlap(floor_mask, offset)
            if point:
                return True
        return False
class FloorSet:
    def __init__(self,x,data):
        self.x = x
        self.data = data
    def move(self):
        self.x -= 10
class Ball:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.jump_vel = 0
        self.img = slime_img
        self.jumping = False
        self.onGround = False
        self.dropTimer = 0
        self.animation_timer = 0
        self.started = False
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    def fall(self):
        if self.started:
            if self.jump_vel > -20:
                self.jump_vel -= 2
            else:
                self.jump_vel = -20
    def jump(self):
        if self.started:
            if self.onGround:
                self.jump_vel = 24
                self.onGround = False
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
    def draw(self,win):
        self.x += self.vel
        self.tilt += (self.vel*-1)*1.8
        self.y -= self.jump_vel
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (round(self.x), round(self.y))).center)
        win.blit(rotated_image,new_rect.topleft)
def draw_window(win,game_speed,bg,balls,floors,rocks,nodeNets,floorSets,lineNets):
    bg.draw(win)
    #scoreTxt = font.render((str(game_speed)), 1, (255,255,255))
    for floorSet in floorSets:
        floorSet.move()
    for floor in floors:
        floor.draw(win)
        floor.move()
    for ball in balls:
        ball.draw(win)
    for rock in rocks:
        rock.draw(win)
    for nodes in nodeNets:
        for node in nodes:
            Circ.draw(node,win)
    for lines in lineNets:
        for line in lines:
            Line.draw(line,win)
    #win.blit(scoreTxt, ((win_width-scoreTxt.get_width()),20))
    pygame.display.update()
def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    random.seed(seed)
    score = 0
    bg = Bg(0)
    balls = []
    floors = []
    floorSets = []
    rocks = []
    win = pygame.display.set_mode((win_width,win_height))
    pygame.display.set_caption("CurI/O")
    game_speed = 24
    play = True
    clock = pygame.time.Clock()
    floor = Floor(1500,775)
    rock = Rock(0,0,5,12)
    rocks.append(rock)
    floors.append(floor)
    floor_clock = 120
    rock_clock = -10
 

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        balls.append(Ball(1000,-1800))
        g.fitness = 0
        ge.append(g)
        
    while play:
        
        clock.tick(game_speed)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
                pygame.quit()
                exit()

        if len(balls) <= 0:
            run = False
            break
 
        #Creating the floors
        r = random.randrange(40,41)
        if floor_clock < r:
            floor_clock += 1
        else:
            data = ""
            picker = random.randrange(0,100)
            if picker >= 40 and picker <= 75:
                floor = Floor(1500,175)
                floors.append(floor)
                data += "1"
            if picker >= 15 and picker <= 70:
                floor = Floor(1500,475)
                floors.append(floor)
                data += "1"
            else:
                if data != "":   
                    data += "0"
            if picker <= 40 or picker >= 70:
                floor = Floor(1500,775)
                floors.append(floor)
                data += "1"
            else:
                if data != "":
                    data += "0"
            floorSet = FloorSet(1500,data)
            floorSets.append(floorSet)

            floor_clock = 0
        #removing the floors
        for floorSet in floorSets:
            if floorSet.x < -550:
                #print(floorSet.data)
                floorSets.remove(floorSet)
                
        for floor in floors:
            if floor.x < -550:
                floors.remove(floor)
                for x, ball in enumerate(balls):
                    ball.started = True
        #creating the rocks
        for rock in rocks:
            if rock.y > 850:
                rocks.remove(rock)
                x = random.randrange(-10,1244)
                y = random.randrange(-100,-50)
                if x > 622:
                    velX = random.randrange(-8,-1)
                    velY = random.randrange(12,20)
                else:
                    velX = random.randrange(1,8)
                    velY = random.randrange(12,20)
                rock = Rock(x,y,velX,velY)
                rocks.append(rock)
        #Moving the balls
        for x, ball in enumerate(balls):
            if ball.y < 0:
                ball.y = 1
            if ball.x < 0:
                ball.x = 0
                ball.vel = 0
            if ball.x > 1130:
                ball.x = 1130
                ball.vel = 0
            for y, floor in enumerate(floors):
                if floor.collide(ball):
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
                    ge[x].fitness -= 2
                    nets.pop(x)
                    ge.pop(x)
                    #print(str(x)+" : died")
            if ball.y > win_height + 75:
                balls.pop(x)
                ge[x].fitness -= 5
                nets.pop(x)
                ge.pop(x)
                #print(str(x)+" : died")
        for rock in rocks:
            rock.move()
        #checking how we should move the balls
        nodeNets = []
        lineNets = []
        for x, ball in enumerate(balls):
            xPos = balls[x].x + 98
            xOffset = 0
            yOffset = 0
            nodes = []
            lines = []
            ge[x].fitness += 0.4
            if len(floorSets) > 4:
                platform = floorSets[math.ceil(((1.5/622)*ball.x))+1].x
                platformData = int(floorSets[math.ceil(((1.5/622)*ball.x)+1)].data)
            else:
                platform = 0
                platformData = 0
            output = nets[x].activate((ball.x,ball.y,rocks[0].x,platform,platformData))

        #============================Drawing Nets START=============================#
            
            for node in ge[x].nodes:
                bias = abs((ge[x].nodes[node]).bias)
                val = bias*100
                if val > 255:
                    val = 255
                color = (val,0,val)
                if output[0] >= 0.55:
                    rColor = (255,255,255)
                else:
                    rColor = color
                if output[1] >= 0.5:
                    lColor = (255,255,255)
                else:
                    lColor = color
                if output[2] >= 0.5:
                    jColor = (255,255,255)   ### TODO FIX THE SPACING OF EVERYTHING
                else:
                    jColor = color
                if ge[x].nodes[node].key == 0:
                    nodes.append(Circ(xPos,(40 + yOffset),rColor,10,ge[x].nodes[node].key))
                    nodes.append(Circ(xPos,(40 + yOffset),color,7,ge[x].nodes[node].key))
                    yOffset += 20
                elif ge[x].nodes[node].key == 1:
                    nodes.append(Circ(xPos,(40 + yOffset),lColor,10,ge[x].nodes[node].key))
                    nodes.append(Circ(xPos,(40 + yOffset),color,7,ge[x].nodes[node].key))
                    yOffset += 20
                elif ge[x].nodes[node].key == 2:
                    nodes.append(Circ(xPos,(40 + yOffset),jColor,10,ge[x].nodes[node].key))
                    nodes.append(Circ(xPos,(40 + yOffset),color,7,ge[x].nodes[node].key))
                    yOffset = 0

                    c1val = math.ceil((255/1244)*ball.x)
                    c1 = (c1val,0,0)
                    nodes.append(Circ((xPos - 70),20,c1,10,-1))

                    c2val = (math.ceil((255/800)*ball.y)-255)*(-1)
                    if c2val < 0:
                        c2val = 0
                    elif c2val > 255:
                        c2val = 255
                    c2 = (0,c2val,0)
                    nodes.append(Circ((xPos - 70),40,c2,10,-2))

                    c3val = math.ceil((255/1244)*rocks[0].x)
                    c3 = (c3val,c3val,c3val)
                    nodes.append(Circ((xPos - 70),60,c3,10,-3))

                    c4val = math.ceil((255/1244)*platform)
                    if c4val < 0:
                        c4val = 0
                    elif c4val > 255:
                        c4val = 255
                    c4 = (c4val,c4val,0)
                    nodes.append(Circ((xPos - 70),80,c4,10,-4))
                    c5val1 = 0
                    c5val2 = 0
                    c5val3 = 0
                    if platformData == 1:
                        c5val1 = 255
                    if platformData == 11:
                        c5val1 = 255
                        c5val2 = 255
                    if platformData == 111:
                        c5val1 = 255
                        c5val2 = 255
                        c5val3 = 255
                    if platformData == 100:
                        c5val3 = 255
                    if platformData == 110:
                        c5val3 = 255
                        c5val2 = 255
                    if platformData == 101:
                        c5val3 = 255
                        c5val1 = 255
                    c5 = (c5val1,c5val2,c5val3)
                    nodes.append(Circ((xPos - 70),100,c5,10,-5))
                    
                    
                else:
                    color = (0,val,val)
                    nodes.append(Circ(xPos-35,(50+yOffset),color,10,ge[x].nodes[node].key))
                    yOffset += 15
                
            nodeNets.append(nodes)
            
            ##### ADDING LINES HERE
            for line in ge[x].connections:
                for y, node in enumerate(nodes):
                    if nodes[y].index == ge[x].connections[line].key[0]:
                        lineX1 = nodes[y].x
                        lineY1 = nodes[y].y 
                    if nodes[y].index == ge[x].connections[line].key[1]:
                        lineX2 = nodes[y].x
                        lineY2 = nodes[y].y
                    

                line = Line(lineX1,lineY1,lineX2,lineY2)
                lines.append(line)

                ##TODO MAYBE GIVE LINE THICKNESS BASED ON BIAS BUT IDK IM LAZY LATELY
            lineNets.append(lines)
                    
                

            ##### ADDING LINES HERE

      
        #=============================Drawing Nets END=============================#
            if output[0] >= 0.55:
                ball.move_right()
                ge[x].fitness -= 0.35
            elif output[1] >= 0.5:
                ball.move_left()
            else:
                ball.vel = 0
                ge[x].fitness -= 0.1
            if output[2] >= 0.5:
                ball.jump()
                ge[x].fitness -= 0.45
            else:
                if not ball.onGround:   
                    ball.fall()
                    ball.jumping = True
                    ge[x].fitness += 1

            
        bg.move()
                
        draw_window(win,clock,bg,balls,floors,rocks,nodeNets,floorSets,lineNets)




def start():
    global GEN
    GEN = 0
    if __name__ == "__main__":
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config.txt")
        run(config_path)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main,2)
    print(winner)
    pygame.quit()
    menu()
if startGame:
    start()

