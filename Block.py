import pygame

class Block:

    def __init__(self, selected_block):
        self.block = selected_block
        self.block_color = selected_block["color"]
        self.block_coords = selected_block["coords"]
        self.shadow_color = selected_block["shadow_color"]
        self.block_pivot = selected_block["pivot"]
        self.kicks = [(-1, 0),(1, 0),(0, -1),(-2, 0),(2, 0),]

    def move_right(self):
        if all(x != 9 for (x, y) in self.block_coords):
            dx, dy = 1, 0
            self.block_coords = {(x + dx, y + dy) for (x, y) in self.block_coords}
            px, py = self.block_pivot
            self.block_pivot = (px + dx, py + dy)

    def move_left(self):
        if all(x != 0 for (x, y) in self.block_coords):
            dx, dy = -1, 0
            self.block_coords = {(x + dx, y + dy) for (x, y) in self.block_coords}
            px, py = self.block_pivot
            self.block_pivot = (px + dx, py + dy)

    def move_down(self, shadow):
        if all(y != 19 for (x, y) in self.block_coords):
            dx, dy = 0, 1
            self.block_coords = {(x + dx, y + dy) for (x, y) in self.block_coords}
            if not shadow:
                px, py = self.block_pivot
                self.block_pivot = (px + dx, py + dy)

    def rotate(self):
        # (1, 1) -> (-1, 1) -> (-1, -1) -> (1, -1) -> (1, 1) -> (-y, x) about the center
        px, py = self.block_pivot
        new_coords = set()
        for x, y in self.block_coords:
            x_new = x - px
            y_new = y - py

            x_rot = -1 * y_new
            y_rot = x_new

            x_final = x_rot + px
            y_final = y_rot + py
            new_coords.add((int(x_final), int(y_final)))
        
        return new_coords

    def check_collisions(self, current_grid, archived_blocks, dy, dx):
        HEIGHT = len(current_grid)          # 20
        WIDTH = len(current_grid[0])        # 10

        occupied = set()
        for shape in archived_blocks:
            occupied |= shape.block_coords

        block_coords_check = {(x + dx, y + dy) for (x, y) in self.block_coords}

        # 1) bounds check
        if any(x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT for (x, y) in block_coords_check):
            return False

        # 2) occupancy check
        if any(occupied & block_coords_check):
            return False

        return True
    
    def check_rotate_collisions(self, current_grid, archived_blocks, coords):
        HEIGHT = len(current_grid)          # 20
        WIDTH = len(current_grid[0])        # 10

        occupied = set()
        for shape in archived_blocks:
            occupied |= shape.block_coords

        # 1) bounds check
        if any(x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT for (x, y) in coords):
            return False

        # 2) occupancy check
        if any(occupied & coords):
            return False

        return True
    
    def check_block_creation(self, archived_blocks):
        occupied = set()
        for shape in archived_blocks:
            occupied |= shape.block_coords

        if any(occupied & self.block_coords):
            return False

        return True
    
    def try_kick_rotate(self, current_grid, archived_blocks, sound, drop_collision_timer):
        original_coords_storage = self.block_coords.copy()
        original_pivot_storage = tuple(self.block_pivot)

        for kx, ky in self.kicks:
            px, py = self.block_pivot

            block_coords_kick = {(x + kx, y + ky) for (x, y) in self.block_coords}
            block_pivot_kick = (px + kx, py + ky)

            self.block_coords = block_coords_kick
            self.block_pivot = block_pivot_kick

            block_coords_kick_rotated = self.rotate()

            valid_kick = self.check_rotate_collisions(
                current_grid,
                archived_blocks,
                block_coords_kick_rotated
            )

            if valid_kick:
                self.block_coords = block_coords_kick_rotated
                self.block_pivot = block_pivot_kick
                sound.play_click()
                drop_collision_timer = 0
                return drop_collision_timer

            self.block_coords = original_coords_storage
            self.block_pivot = original_pivot_storage

        return drop_collision_timer
    
    def shadow_coordinates(self, shadow_block, archived_blocks, current_grid):
        HEIGHT = len(current_grid)

        shadow_block.block_coords = set(self.block_coords)

        # Can't fall more than HEIGHT rows. Safety cap prevents any “fall off board” hangs.
        for _ in range(HEIGHT):
            if shadow_block.check_collisions(current_grid, archived_blocks, 1, 0):
                shadow_block.move_down(shadow=True)
            else:
                break
