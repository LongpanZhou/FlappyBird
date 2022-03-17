import pygame
import neat
import time
import os
import random
import math
pygame.init()
pygame.display.set_caption("Flappy Bird")
pygame.display.set_icon(pygame.image.load(os.path.join("imgs","bird1.png")))

WIN_WIDTH = 575
WIN_HEIGHT = 800
max_score = 0
pause = False

birdImg = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
pipeImg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
baseImg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
backgroundImg = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
button_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird_button.png")))
home_img = pygame.image.load(os.path.join("imgs","home.png"))
quit_img = pygame.image.load(os.path.join("imgs","quit.png"))
restart_img = pygame.image.load(os.path.join("imgs","restart.png"))
unpause_img = pygame.image.load(os.path.join("imgs","unpause.png"))

Font = pygame.font.SysFont("arialblack",50)
small_font = pygame.font.SysFont("arialblack",20)

class button():
	def __init__(self,x,y,image,ids):
		self.img = image
		self.rect = self.img.get_rect()
		self.rect.topleft = (x,y)
		self.id = ids

	def draw(self,win):
		pos = pygame.mouse.get_pos()

		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				if self.id == 0:
						local_dir = os.path.dirname(__file__)
						config_path = os.path.join(local_dir, "config-feedforward.txt")
						run(config_path)
				elif self.id == 1:
					intro(0)
				elif self.id == 2:
					pygame.quit()
					quit()
				elif self.id == 3:
					player()
				elif self.id == 4:
					global pause
					pause = False

		win.blit(self.img, (self.rect.x, self.rect.y))


class Bird:
	IMGS = birdImg
	maxRotation = 25
	rottateVel = 20
	animationTime = 5

	def __init__(self,x,y):
		self.x = x 
		self.y = y 
		self.tilt = 0 
		self.tick_count = 0 
		self.vel = 0
		self.height = self.y 
		self.img_count = 0
		self.img = self.IMGS[0]
		self.gravity = 7.63

	def jump(self):
		self.vel = -5.34
		self.tick_count = 0
		self.height = self.y 

	def move(self):
		self.tick_count+=1
		
		#projectile
		self.vel = self.vel + self.tick_count/60*self.gravity
		d = self.vel * self.tick_count

		#vel max and min 
		if d >= 8.875:
			d = 8.875

		if d < 0:
			d -=2
			
		#update position
		self.y = self.y + d

		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.maxRotation:
				self.tilt = self.maxRotation
		else:
			if self.tilt >-90:
				self.tilt -= self.rottateVel

	def draw(self, win):
		self.img_count+=1

		if self.img_count < self.animationTime:
			self.img = self.IMGS[0]
		elif self.img_count < self.animationTime*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.animationTime*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.animationTime*4:
			self.img = self.IMGS[1]	
		else:
			self.img =self.IMGS[0]
			self.img_count = 0;
		
		#displace tilt img
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.animationTime*2
		
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
		win.blit(rotated_image,new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	Gap = 200
	Vel = 5

	def __init__(self, x):
		self.x = x 
		self.height = 0
		self.top = 0 
		self.bottom = 0 
		self.PIPE_TOP = pygame.transform.flip(pipeImg, False, True)
		self.PIPE_BOTTOM = pipeImg

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50,450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.Gap

	def move(self):
		self.x -= self.Vel

	def draw(self, win):
		win.blit(self.PIPE_TOP,(self.x,self.top))
		win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))

	def collide(self, bird):
                #check if the mask covers eachother
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		t_point = bird_mask.overlap(top_mask, top_offset)
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)

		if t_point or b_point:
			return True
		return False

class Base:
	Vel = 5
	Width = baseImg.get_width()
	IMG = baseImg
	
	def __init__(self,y):
		self.y = y 
		self.x1 = 0 
		self.x2 = self.Width 

	def move(self):
		self.x1 -= self.Vel
		self.x2 -= self.Vel

		if self.x1 + self.Width < 0:
			self.x1 = self.x2 + self.Width
		if self.x2 + self.Width < 0:
			self.x2 = self.x1 + self.Width

	def draw(self,win):
		win.blit(self.IMG,(self.x1,self.y))
		win.blit(self.IMG,(self.x2,self.y))

def draw_window(win, birds, pipes, base, score, intro):
	win.blit(backgroundImg,(0,0))
	for pipe in pipes:
		pipe.draw(win)

	if intro == True:
		global max_score
		max_score_text = small_font.render("Max Score:" + str(max_score), 1, (255,255,255))
		instruction_text1 = small_font.render("Press Space to Start", 1, (255,255,255))
		instruction_text2 = small_font.render("Press Esc to pause", 1, (255,255,255))

		win.blit(max_score_text , (WIN_WIDTH/2 - max_score_text.get_width()/2, WIN_HEIGHT/2-100))
		win.blit(instruction_text1 , (WIN_WIDTH/2 - instruction_text1.get_width()/2, WIN_HEIGHT/2+50))
		win.blit(instruction_text2 , (WIN_WIDTH/2 - instruction_text2.get_width()/2, WIN_HEIGHT/2+75))

		start_button = button(0,0, button_img,0)
		start_button.draw(win)

	text = Font.render(str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH/2 - text.get_width()/2, WIN_HEIGHT/2-200))

	for bird in birds:
		bird.draw(win)
	base.draw(win)
	pygame.display.update()

def player():
	bird = [Bird(250,350)]
	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	clock = pygame.time.Clock()
	score = 0
	add_pipe = False

	run = True
	while run:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			elif (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or (pygame.mouse.get_pressed()[0]==1):
				bird[0].jump()
			elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
				Pause(win)
		bird[0].move()

		for pipe in pipes:
			if pipe.collide(bird[0]):
				intro(score)
			if not pipe.passed and pipe.x < bird[0].x:
				pipe.passed = True
				add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				pipes.pop(0)

			pipe.move()

		if add_pipe:
			score +=1
			pipes.append(Pipe(600))	
			add_pipe = False

		if bird[0].y + bird[0].img.get_height() >= 730 or bird[0].y < 0 :
			intro(score)
		
		base.move()
		draw_window(win,bird,pipes,base,score,False)
		
def AI(genomes, config):
	birds = []
	ge = []
	nets = []

	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	clock = pygame.time.Clock()

	for _,g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g,config)
		nets.append(net)
		birds.append(Bird(230,350))
		g.fitness = 0
		ge.append(g)

	score = 0
	add_pipe = False

	run = True
	while run:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		index = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				index = 1
		else:
			run = False
			break

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.01
			output = nets[x].activate((bird.y,abs(bird.y - pipes[index].height), abs(bird.y - pipes[index].bottom)))

			if output[0] > 0.5:
				bird.jump()

		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= 1
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				pipes.pop(0)

			pipe.move()

		if add_pipe:
			score +=1
			for g in ge:
				g.fitness += 1.5
			pipes.append(Pipe(600))	
			add_pipe = False

		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		base.move()
		draw_window(win,birds,pipes,base,score,False)

def Pause(win):
	global pause
	pause = True
	while pause:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pause = False

		home_button = button(WIN_WIDTH/2-home_img.get_width()/2,WIN_HEIGHT/2-100,home_img,1)
		home_button.draw(win)
		quit_button = button(WIN_WIDTH/2-quit_img.get_width()/2,WIN_HEIGHT/2,quit_img,2)
		quit_button.draw(win)
		restart_button = button(WIN_WIDTH/2-restart_img.get_width()/2,WIN_HEIGHT/2+100,restart_img,3)
		restart_button.draw(win)
		unpause_button = button(WIN_WIDTH/2-unpause_img.get_width()/2,WIN_HEIGHT/2+200,unpause_img,4)
		unpause_button.draw(win)

		pygame.display.update()

def intro(score):
	intro = True
	bird = [Bird(250,350)]
	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	clock = pygame.time.Clock()

	base.move()
	global max_score
	max_score = max(score,max_score)

	while intro == True:
		clock.tick(60)
		ticks = pygame.time.get_ticks()
		draw_window(win,bird,pipes,base,0,True)
		bird[0].y = 350 + math.sin(ticks*0.005)*25
		for event in pygame.event.get():
			if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
				player()
				intro = False
			if event.type == pygame.QUIT:
                                pygame.QUIT()
                                quit()

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
	p = neat.Population(config)

        #---print reports of NEAT in terminal---
	#p.add_reporter(neat.StdOutReporter(True))
	#stats = neat.StatisticsReporter()
	#p.add_reporter(stats)

	winner = p.run(AI,50)
if __name__ == '__main__':
	intro(0)
