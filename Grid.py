import pygame

class Grid:

    def __init__(self, x_blocks, y_blocks, screen_width, screen_height, block_size):

        self.x_blocks = x_blocks
        self.y_blocks = y_blocks

        self.block_distance = block_size * 1.1

        self.starting_x = screen_width/2 - ((self.x_blocks/2)*self.block_distance)
        self.starting_y = screen_height/2 - ((self.y_blocks/2)*self.block_distance) + 100

        self.unoccupied_block_color = (50, 50, 50)
        self.grid = [[self.unoccupied_block_color for x in range(self.x_blocks)] for y in range(self.y_blocks)]
  
    def update_grid(self, active_block, archived_blocks, shadow_block):

        active_block_color = active_block.block_color
        active_block_coords = active_block.block_coords
        for x in range(self.x_blocks):
            for y in range(self.y_blocks):
                if (x, y) in active_block_coords:
                        self.grid[y][x] = active_block_color
                else:
                    if (x, y) in shadow_block.block_coords:
                        self.grid[y][x] = shadow_block.shadow_color
                    else:
                        self.grid[y][x] = self.unoccupied_block_color 
                    for archived_block in archived_blocks:
                        archived_block_color = archived_block.block_color
                        archived_block_coords = archived_block.block_coords
                        if (x, y) in archived_block_coords:
                            self.grid[y][x] = archived_block_color

        return self.grid

    def draw_grid(self, screen, block_size, current_grid):
        pygame.draw.rect(screen, (0,0,0), (self.starting_x, self.starting_y, self.x_blocks*self.block_distance, self.y_blocks*self.block_distance))
        for x in range(self.x_blocks):
            for y in range(self.y_blocks):
                pygame.draw.rect(screen, current_grid[y][x], (self.starting_x + self.block_distance * x, self.starting_y + self.block_distance * y, block_size, block_size))
            


    def clear_rows(self, current_grid, archived_blocks):

        index = 0
        rows_cleared = 0
        for row in current_grid:
            if all(cell != self.unoccupied_block_color for cell in row):
                current_grid[index] = [self.unoccupied_block_color] * 10
                for archived_block in archived_blocks:
                    archived_block.block_coords = {(x, y) for (x, y) in archived_block.block_coords if y != index}
                rows_cleared += 1
            index+=1

        return rows_cleared
        
    def move_rows(self, current_grid, archived_blocks):

        movable_rows = True
        while movable_rows:
            movable_rows_count = 0
            for index in range(len(current_grid)-1):
                if all(cell == self.unoccupied_block_color for cell in current_grid[index+1]) and any(cell != self.unoccupied_block_color for cell in current_grid[index]):
                    current_grid[index+1] = current_grid[index]
                    current_grid[index] = [self.unoccupied_block_color] * 10
                    for archived_block in archived_blocks:
                        archived_block.block_coords = {(x, y+1) if y == index else (x, y) for (x, y) in archived_block.block_coords}
                    movable_rows_count += 1
            if movable_rows_count == 0:
                movable_rows = False
