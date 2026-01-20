import pygame

class Next_Block_Grid:

    def __init__(self, x_blocks, y_blocks, screen_width, screen_height, block_size):

        self.x_blocks = x_blocks
        self.y_blocks = y_blocks

        self.block_distance = block_size * 1.1

        self.starting_x = screen_width/(4/3)
        self.starting_y = screen_height/2 - ((10)*self.block_distance) + 200

        self.unoccupied_block_color = (50, 50, 50)
        self.next_block_grid = [[self.unoccupied_block_color for x in range(self.x_blocks)] for y in range(self.y_blocks)]
  
    def update_grid(self, next_block):
        self.next_block_grid = [[self.unoccupied_block_color for x in range(self.x_blocks)] for y in range(self.y_blocks)]
        next_block_color = next_block["color"]
        next_block_coords = next_block["coords"]
        for x in range(self.x_blocks):
            for y in range(self.y_blocks):
                if (x, y) in next_block_coords:
                        self.next_block_grid[y][x-2] = next_block_color
                

        return self.next_block_grid

    def draw_grid(self, screen, block_size, next_block_grid):

        for x in range(self.x_blocks):
            for y in range(self.y_blocks):
                #if next_block_grid[y][x] != self.unoccupied_block_color:
                if x <6:
                    rect = pygame.Rect(0, 0, block_size, block_size)
                    rect.topleft = (
                        self.starting_x + self.block_distance * x,
                        self.starting_y + self.block_distance * y
                    )
                    pygame.draw.rect(screen, next_block_grid[y][x], rect)                    
                    #pygame.draw.rect(screen, next_block_grid[y][x], (self.starting_x + self.block_distance * x, self.starting_y + self.block_distance * y, block_size, block_size))