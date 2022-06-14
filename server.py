#!/usr/bin/python3

import threading
import socket
import time
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
FORMAT = 'utf-8'

first = False
LEFT_SCORE = 0
RIGHT_SCORE = 0
#Modules
import pygame
pygame.init()

#GLOBAL PARAMS
WIDTH = 700
HEIGHT = 500

PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100

BALL_RADIUS = 7


BOARD = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("PONG")

FPS = 60

WHITE = (255,255,255)
BLACK = (0,0,0)

SCORE_FONT = pygame.font.SysFont("comicsans",50)

CONNECTED_PLAYERS = 0

WINNING_SCORE = 10


def handle_client(conn,paddle):
	prev = ""
	while True:
		dataPair = conn.recvfrom(2)
		data = dataPair[0].decode(FORMAT).rstrip('\x00')
		addr = dataPair[1] 
		print(data)
		score = (f"{LEFT_SCORE} : {RIGHT_SCORE}")
		if prev != score :
			print(score.encode(FORMAT))
			conn.sendto(score.encode(FORMAT), addr)
			prev = score
		if not data:
			break
		if data == "U":
			paddle.move(up=True)
			paddle.move(up=True)
	
		elif data == "D":
			paddle.move(up=False)
			paddle.move(up=False)
		#print(data.decode(FORMAT))\


class Paddle:
	COLOR = WHITE
	VELOCITY  = 40

	def __init__(self, x , y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height

		#Set original x & y to reset
		self.x_initial = x
		self.y_initial = y

	def draw(self, board):
		pygame.draw.rect(board, self.COLOR, (self.x, self.y, self.width, self.height))

	def move(self, up):
		if up:
			self.y = self.y - self.VELOCITY
		else:
			self.y = self.y + self.VELOCITY
	def reset(self):
		self.x = self.x_initial
		self.y = self.y_initial


class Ball:
	COLOR = WHITE
	MAX_VEL = 5

	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.radius = radius
		self.x_vel = self.MAX_VEL
		self.y_vel = 0

		#Set original x & y to reset
		self.x_initial = x
		self.y_initial = y

	def draw(self,board):
		pygame.draw.circle(board, self.COLOR, (self.x, self.y), self.radius)

	def move(self):
		self.x = self.x + self.x_vel
		self.y = self.y + self.y_vel

	def reset(self):
		self.x = self.x_initial
		self.y = self.y_initial
		self.y_vel = 0
		self.x_vel = self.x_vel * (-1)

def draw(board, paddles, ball):
	board.fill(BLACK)

	left_score_text = SCORE_FONT.render(f"{LEFT_SCORE}", 1, WHITE)
	right_score_text = SCORE_FONT.render(f"{RIGHT_SCORE}", 1, WHITE)
	board.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2,20))
	board.blit(right_score_text, ((WIDTH//4)*3 - left_score_text.get_width()//2,20))

	for paddle in paddles:
		paddle.draw(BOARD)

	ball.draw(BOARD)
	pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle):
	if ball.y + ball.radius >= HEIGHT:
		ball.y_vel = ball.y_vel * (-1)
	elif ball.y - ball.radius <= 0:
		ball.y_vel = ball.y_vel * (-1)

	if ball.x_vel < 0:
		#Check if ball hits left paddle
		if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
			if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
				ball.x_vel = ball.x_vel * (-1)

				middle_y = left_paddle.y + left_paddle.width/2
				difference_in_y = middle_y - ball.y
				reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
				y_vel = difference_in_y / reduction_factor
				ball.y_vel = (-1) * y_vel
	else:
		#Check if ball hits right paddle
		if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
			if ball.x + ball.radius >= right_paddle.x:
				ball.x_vel = ball.x_vel * (-1)

				middle_y = right_paddle.y + right_paddle.width/2
				difference_in_y = middle_y - ball.y
				reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
				y_vel = difference_in_y / reduction_factor
				ball.y_vel = (-1) * y_vel

def handle_paddle_movement(keys, left_paddle, right_paddle):
	if keys[pygame.K_w] and left_paddle.y > 0:
		left_paddle.move(up=True)
	if keys[pygame.K_s] and left_paddle.y + PADDLE_HEIGHT < HEIGHT:
		left_paddle.move(up=False)
	
	if keys[pygame.K_UP] and right_paddle.y > 0:
		right_paddle.move(up=True)
	if keys[pygame.K_DOWN] and right_paddle.y + PADDLE_HEIGHT < HEIGHT:
		right_paddle.move(up=False)


def main():
	global LEFT_SCORE, RIGHT_SCORE

	run = True
	wait = True
	clock = pygame.time.Clock()

	left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2,PADDLE_WIDTH,PADDLE_HEIGHT)
	right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2,PADDLE_WIDTH,PADDLE_HEIGHT)
	ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)



	##### Player 1 - SOCKET

	s =  socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	s.bind((HOST, PORT))
	thread = threading.Thread(target=handle_client, args=(s,left_paddle), daemon=True)
	thread.start()
	#########

	##### Player 2 - SOCKET

	s2 =  socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	s2.bind((HOST, 65443))
	thread2 = threading.Thread(target=handle_client, args=(s2,right_paddle), daemon=True)
	thread2.start()
	#########


	wait_msg = SCORE_FONT.render(f"Waiting for players", 1, WHITE)
	start_msg = SCORE_FONT.render(f"Game starts in: 3s.",1,WHITE)

	p1_ready_msg = SCORE_FONT.render(f"Plater 1 Ready", 1, WHITE)
	p2_ready_msg = SCORE_FONT.render(f"Player 2 Ready", 1, WHITE)

	while wait:
		clock.tick(FPS)
		BOARD.fill(BLACK)
	
	
		BOARD.blit(wait_msg, (WIDTH//2 - wait_msg.get_width()//2,20))

		if CONNECTED_PLAYERS == 1:
			BOARD.blit(p1_ready_msg, (WIDTH//4 - p1_ready_msg.get_width()//2,250))

		elif CONNECTED_PLAYERS == 2:
			BOARD.blit(p2_ready_msg, ((WIDTH//4)*3 - p2_ready_msg.get_width()//2,20))
			BOARD.blit(start_msg, (WIDTH//2 - start_msg.get_width()//2,20))
			wait=False
			pygame.time.wait(3000)

		pygame.display.update()


	while run:

		clock.tick(FPS)
		draw(BOARD,[left_paddle,right_paddle], ball)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		keys = pygame.key.get_pressed()
		handle_paddle_movement(keys, left_paddle, right_paddle)
		ball.move()
		handle_collision(ball, left_paddle, right_paddle)

		if ball.x <= 0:
			RIGHT_SCORE += 1
			ball.reset()
		elif ball.x >= WIDTH:
			LEFT_SCORE += 1
			ball.reset()

		won = False

	if LEFT_SCORE >= WINNING_SCORE:
		won = True
		win_text = "Left Player Won!"
	elif RIGHT_SCORE >= WINNING_SCORE:
		won = True
		win_text = "Right Player Won!"

	if won:
		text = SCORE_FONT.render(win_text, 1, WHITE)
		BOARD.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
		pygame.display.update()
		pygame.time.delay(5000)
		ball.reset()
		left_paddle.reset()
		right_paddle.reset()
		LEFT_SCORE = 0
		RIGHT_SCORE = 0


	pygame.quit()

	



if __name__ == '__main__':
	main()
