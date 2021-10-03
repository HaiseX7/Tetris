import pygame
import sys
import random
import numpy as np
import pygame.font
from threading import Timer

""" GET RID OF THE TIMER OBJECTS AND REPLACE
THEM WITH A CLOCK ITERATION THAT DOESNT RELY
ON A MILLION FLAGS."""

class Tetris:

	def __init__(self):
		# Initialize pygame module
		pygame.init()

		# Initialize the screen
		self.screen = pygame.display.set_mode((1200, 800))

		# Create an instance of the grid
		self.grid = Grid(self)

		# Define a list of the blocks that will be in play
		self.blocks = []

		# Flag for if a block is active on the playing field
		# Flag for if a block is finished 
		self.block_active = False
		self.block_finish = False

		# Flag for the incremental downward movement clock
		self.clock_active = False

		# List that stores all the finished blocks
		# This will be utilized for collision detection
		self.finished_blocks = []

		self.unaccepted_coordinates = []

		self.label = Label(self.screen)

		self.count = 0

	def run_game(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					self.check_keydown_events(event)

			""" This is the collision detection logic
			Once there is more than one block collisions can occur
			Finished blocks are stored in a list and collisions are detected
			between the new piece and the culmination of all old pieces """
			if len(self.blocks) > 1:
				self.manage_finished_blocks()
				self.check_collisions(self.finished_blocks_grid)
				self.check_unaccepted_coords(self.finished_blocks_grid)

			# Creates a block if no block is currently active
			if not self.block_active:
				self.create_block()

			# Conditional statement for incrementing block movement
			if not np.any(self.piece.color_grid[19]) and len(self.blocks) == 1:
				self.increment_movement()
			elif np.any(self.piece.color_grid[19]):
				self.block_active = False

			# Sets the grid equal to the sum of all the blocks
			self.grid.block_color_list = sum(self.blocks)

			self.display_screen()	

	def check_keydown_events(self, event):
		if event.key == pygame.K_DOWN:
			if not np.any(self.piece.color_grid[19]):
				self.piece.move_down()
				if not self.check_valid_space():
					self.piece.move_up()
		elif event.key == pygame.K_LEFT:
			if not np.any(self.piece.color_grid[:, 0]):
				self.piece.move_left()
				if not self.check_valid_space():
					self.piece.move_right()
		elif event.key == pygame.K_RIGHT:
			if not np.any(self.piece.color_grid[:, 9]):
				self.piece.move_right()
				if not self.check_valid_space():
					self.piece.move_left()
		elif event.key == pygame.K_q:
			sys.exit()

	def manage_finished_blocks(self):
		for x in range(len(self.blocks) - 1):
			self.finished_blocks.append(self.blocks[x])
		self.finished_blocks_grid = sum(self.finished_blocks)

	def check_valid_space(self):
		for y in range(20):
			for x in range(10):
				if np.any(self.piece.color_grid[y][x]):
					coord = (x, y)
					if coord in self.unaccepted_coordinates:
						return False
		return True

	def increment_movement(self):
		if not self.clock_active and self.block_active:
			self.t = Timer(1.0, self.piece.move_down)
			self.t.start()
			self.clock_active = True
		if not self.t.is_alive():
			self.clock_active = False

	def check_collisions(self, finished_blocks_grid):
		self.check_down_collision(finished_blocks_grid)

	def check_down_collision(self, finished_blocks_grid):
		for y in reversed(range(20)):
			for x in range(10):
				if np.any(self.piece.color_grid[y][x]): 
					if y < 19:
						if np.any(finished_blocks_grid[y+1][x]):
							self.t.cancel()
							self.block_active = False
						else:
							self.increment_movement()
				else:
					pass

	def check_unaccepted_coords(self, finished_blocks_grid):
		self.unaccepted_coordinates = []
		for y in range(20):
			for x in range(10):
				if np.any(finished_blocks_grid[y][x]):
					coord = (x, y)
					self.unaccepted_coordinates.append(coord)

	def create_block(self):
		self.piece = Piece()
		self.blocks.append(self.piece.color_grid)
		self.block_active = True

	def display_screen(self):
		self.screen.fill((200, 200, 200))
		self.screen.fill((115, 115, 115),pygame.Rect(445, 180, 10*31, 20*31))
		self.grid.create_grid()
		self.label.blit()
		pygame.display.flip()


class Pieces:
	""" CREATE THE PIECES AND PASS IT TO PIECE """
	def __init__(self):
		X = [255, 0, 0]
		y = (0, 0, 255)
		z = (0, 255, 0)
		W = (0, 255, 255)
		Q = (255, 255, 0)
		o = (0, 0, 0)
		self.piece1 = np.array(
					  [[o, o, o, o, X, X, o, o, o, o],
					   [o, o, o, o, o, X, o, o, o, o],
					   [o, o, o, o, o, X, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o]])
		self.piece2 = np.array(
					  [[o, o, o, y, y, o, o, o, o, o],
					   [o, o, o, y, y, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o]])
		self.piece3 = np.array(
					  [[o, o, o, o, z, o, o, o, o, o],
					   [o, o, o, o, z, o, o, o, o, o],
					   [o, o, o, o, z, o, o, o, o, o],
					   [o, o, o, o, z, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o]])
		self.piece4 = np.array(
					  [[o, o, o, o, o, W, o, o, o, o],
					   [o, o, o, o, W, W, o, o, o, o],
					   [o, o, o, o, o, W, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o]])
		self.piece5 = np.array(
					  [[o, o, o, o, o, Q, Q, o, o, o],
					   [o, o, o, o, Q, Q, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o],
					   [o, o, o, o, o, o, o, o, o, o]])
		self.shapes = [self.piece1, self.piece2, self.piece3, self.piece4, self.piece5]


class Piece:

	def __init__(self):
		self.pieces = Pieces()
		self.color_grid = self.pieces.shapes[random.randint(0, len(self.pieces.shapes) - 1)]

	def move_down(self):
		count = 0
		for y in reversed(range(20)):
			for x in reversed(range(10)):
				if count <= 4:
					if np.any(self.color_grid[y][x]):
						self.color_grid[y+1][x] = self.color_grid[y][x]
						self.color_grid[y][x] = (0, 0, 0)
						count+=1
					else:
						pass

	def move_left(self):
		count = 0
		for y in range(20):
			for x in range(10):
				if count <= 4:
					if np.any(self.color_grid[y][x]):
						self.color_grid[y][x-1] = self.color_grid[y][x]
						self.color_grid[y][x] = (0, 0, 0)
						count+=1
					else:
						pass

	def move_right(self):
		count = 0
		for y in range(20):
			for x in reversed(range(10)):
				if count <= 4:
					if np.any(self.color_grid[y][x]):
						self.color_grid[y][x+1] = self.color_grid[y][x]
						self.color_grid[y][x] = (0, 0, 0)
						count+=1
					else:
						pass

	def move_up(self):
		count = 0
		for y in range(20):
			for x in range(10):
				if count <=4:
					if np.any(self.color_grid[y][x]):
						self.color_grid[y-1][x] = self.color_grid[y][x]
						self.color_grid[y][x] = (0, 0, 0)


class Grid:

	def __init__(self, tetris):
		self.grid_height = 20
		self.grid_width = 10
		self.block_width, self.block_height = (30, 30)
		self.screen = tetris.screen
		self.block_list = [[pygame.Rect(0, 0, 0, 0) for x in range(10)] for y in range(20)]
		self.block_color_list = np.array([[(0, 0, 0) for x in range(10)] for y in range(20)])

	def create_grid(self):
		for row_num in range(self.grid_height):
			for col_num in range(self.grid_width):
				self.create_block(row_num, col_num)

	def create_block(self, row_num, col_num):
		self.rect = pygame.Rect(0, 0, self.block_height, self.block_width)
		self.rect.x = 445 + (col_num * 31)
		self.rect.y = 180 + (row_num * 31)
		self.block = pygame.draw.rect(self.screen, self.block_color_list[row_num][col_num], self.rect)
		self.block_list[row_num][col_num] = self.rect


class Label:

	def __init__(self, tetris_screen):
		pygame.font.init()
		self.screen = tetris_screen
		self.font = pygame.font.SysFont('comicsans', 60)
		self.label = self.font.render('Tetris', 1, (20, 20, 20))

	def blit(self):
		self.screen.blit(self.label, (600 - 0.5 * self.label.get_width(), 30))


if __name__ == '__main__':
	tetris = Tetris()
	tetris.run_game()
