import pygame
import os
from sound_design import SoundDesign
from Next_Bock_Grid import Next_Block_Grid
from Block import Block
from Blocks import Blocks
from Grid import Grid
from Button import Button
from supabase import create_client, Client
from dotenv import load_dotenv
from GameState import GameState

class Game:
    
    def __init__(self):
        # =========================
        # CONFIG / CONSTANTS
        # =========================

        # --- Global UI scale (everything that multiplies by this is “resolution dependent”) ---
        self.scale_factor = 0.6

        # --- Grid dimensions (logical board size) ---
        self.X_BLOCKS = 10
        self.Y_BLOCKS = 20

        # --- Timing (ms) ---
        self.DROP_INTERVAL_MS     = 1000
        self.LOCK_DELAY_MS        = 1000
        self.MAX_LOCK_DELAY_MS    = 4000
        self.TOTAL_LEVEL_DURATION_MS = 6_000

        # --- Overlay / UI ---
        self.OVERLAY_ALPHA = 200

        # --- Lock-bar visuals (scaled) ---
        self.LOCK_BAR_WIDTH  = 200 * self.scale_factor
        self.LOCK_BAR_HEIGHT = 12  * self.scale_factor
        self.LOCK_BAR_BG     = (60, 60, 60)  # dark gray


        # =========================
        # PYGAME INIT + DISPLAY
        # =========================

        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Tetris")

        # Display info + fullscreen surface
        self.infoObject   = pygame.display.Info()
        self.SCREEN_WIDTH = self.infoObject.current_w
        self.SCREEN_HEIGHT = self.infoObject.current_h

        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.FULLSCREEN
        )
        self.clock = pygame.time.Clock()

        # Size of one grid “cell” in pixels (scaled)
        self.GRID_BLOCK_SIZE = 50 * self.scale_factor


        # =========================
        # OVERLAY + FONTS + STATIC TEXT
        # =========================

        # Semi-transparent overlay for menus / pause / game over
        self.overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, self.OVERLAY_ALPHA))

        # Fonts (scaled)
        self.font_title = pygame.font.SysFont("Arial", int(90 * self.scale_factor))
        self.font_ui    = pygame.font.SysFont("Arial", int(45 * self.scale_factor))

        # Pre-rendered title surface
        self.tetris_surface = self.font_title.render("Tetris", True, (255, 255, 255))


        # =========================
        # ASSETS (IMAGES / PATHS)
        # =========================

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Background
        self.background_path = os.path.join(self.BASE_DIR, "Tetris Image.png")
        self.background      = pygame.image.load(self.background_path)
        self.background_rect = self.background.get_rect()
        self.background_rect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)

        # In-game logo
        self.logo_path = os.path.join(self.BASE_DIR, "Tetris Logo 0.75.jpg")
        self.logo      = pygame.image.load(self.logo_path)
        self.logo      = pygame.transform.scale_by(self.logo, self.scale_factor)
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.center = (self.SCREEN_WIDTH // 2, 150 * self.scale_factor)

        # Main menu logo
        self.main_menu_logo_path = os.path.join(self.BASE_DIR, "Tetris Logo.jpg")
        self.main_menu_logo      = pygame.image.load(self.main_menu_logo_path)
        self.main_menu_logo      = pygame.transform.scale_by(self.main_menu_logo, self.scale_factor)
        self.main_menu_logo_rect = self.main_menu_logo.get_rect()
        self.main_menu_logo_rect.center = (self.SCREEN_WIDTH // 2, 200 * self.scale_factor)


        # =========================
        # PLAYER / NAME ENTRY
        # =========================

        self.player_name    = ""
        self.entering_name  = False
        self.MAX_NAME_LEN   = 12


        # =========================
        # MAIN MENU BUTTONS
        # =========================

        center_x = self.SCREEN_WIDTH // 2

        self.start_game_menu_option = Button(
            self.screen, "Start Game", (center_x, 600 * self.scale_factor)
        )
        self.leaderboard_menu_option = Button(
            self.screen, "LeaderBoard", (center_x, 800 * self.scale_factor)
        )
        self.quit_game_menu_option = Button(
            self.screen, "Quit Game", (center_x, 1000 * self.scale_factor)
        )

        # Resolution toggles (offset left/right)
        self.ultrawide_menu_option = Button(
            self.screen, "Ultrawide Res", (center_x - 200, 1200 * self.scale_factor)
        )
        self.laptop_menu_option = Button(
            self.screen, "Laptop Res", (center_x + 200, 1200 * self.scale_factor)
        )

        # UI text placeholders
        self.timer_text = ""


        # =========================
        # GAME OBJECTS
        # =========================

        self.grid = Grid(
            self.X_BLOCKS,
            self.Y_BLOCKS,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.GRID_BLOCK_SIZE
        )

        self.next_block_grid = Next_Block_Grid(
            8, 3, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.GRID_BLOCK_SIZE
        )

        self.blocks = Blocks()

        self.sound = SoundDesign()
        self.sound.play_music()

        # Handy references / state containers
        self.current_grid    = self.grid.grid
        self.archived_blocks = []


        # =========================
        # GAME STATE (RUNTIME VARIABLES)
        # =========================

        # Score / progression
        self.points = 0
        self.level  = 1

        # Active piece bookkeeping
        self.is_active_block = False
        self.next_block      = None
        self.new_block       = []

        # Timers (ms accumulation)
        self.drop_timer                   = 0
        self.drop_collision_timer        = 0
        self.forced_drop_collision_timer = 0
        self.dt = 0

        # Level clock
        self.level_time_ms     = 0
        self.level_duration_ms = self.TOTAL_LEVEL_DURATION_MS

        # Collision / locking flags
        self.collision_reached = False

        # High-level state machine
        self.game_state = GameState.MAIN_MENU
        self.running    = True

    def main_menu(self):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.main_menu_logo, self.main_menu_logo_rect)

        self.start_game_menu_option.draw_button()
        self.leaderboard_menu_option.draw_button()
        self.quit_game_menu_option.draw_button()
        self.ultrawide_menu_option.draw_button()
        self.laptop_menu_option.draw_button()

    def leaderboard(self, data):

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.main_menu_logo, self.main_menu_logo_rect)

        title = self.font_title.render("LEADERBOARD", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(midtop=(self.SCREEN_WIDTH//2, 450*self.scale_factor)))

        # Column headers
        header = self.font_ui.render("RANK   NAME            SCORE", True, (200, 200, 200))
        self.screen.blit(header, (self.SCREEN_WIDTH//2 - 250, 600*self.scale_factor))

        y = 650*self.scale_factor
        for i, r in enumerate(data, start=1):
            name = (r["Username"] or "")[:12]  # truncate to fit
            score = r["Score"]
            line = f" {i:>2}         {name:<12}  {score:>8}"
            surf = self.font_ui.render(line, True, (255, 255, 255))
            self.screen.blit(surf, (self.SCREEN_WIDTH//2 - 250, y))
            y += 42

        query_menu_surface = self.font_ui.render("Press R to return to Refresh Leaderboard", True, (255, 255, 255))
        self.screen.blit(query_menu_surface, query_menu_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 600*self.scale_factor)))
        return_main_menu_surface = self.font_ui.render("Press M to return to Main Menu", True, (255, 255, 255))
        self.screen.blit(return_main_menu_surface, return_main_menu_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 700*self.scale_factor)))

    def game_running(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, self.logo_rect)
        current_grid = self.grid.update_grid(self.block, self.archived_blocks, self.shadow_block)
        next_block_grid_data = self.next_block_grid.update_grid(self.next_block)
        self.block.shadow_coordinates(self.shadow_block, self.archived_blocks, current_grid)
        self.grid.draw_grid(self.screen, self.GRID_BLOCK_SIZE, current_grid)
        self.next_block_grid.draw_grid(self.screen, self.GRID_BLOCK_SIZE, next_block_grid_data)

        points_surface = self.font_ui.render("Score: " + str(self.points), True, (255, 255, 255))
        level_surface = self.font_ui.render("Level: " + str(self.level), True, (255, 255, 255))
        timer_surface = self.font_ui.render("Timer: " + self.timer_text, True, (255, 255, 255))
        next_block_surface = self.font_ui.render("Next Block: ", True, (255, 255, 255))
        self.screen.blit(points_surface, points_surface.get_rect(topleft=(self.SCREEN_WIDTH//4, self.SCREEN_HEIGHT/2 - ((self.Y_BLOCKS/2)*self.grid.block_distance) + 100)))
        self.screen.blit(timer_surface, timer_surface.get_rect(topleft=(self.SCREEN_WIDTH//4, self.SCREEN_HEIGHT/2 - ((self.Y_BLOCKS/2)*self.grid.block_distance) + 100+120)))
        self.screen.blit(level_surface, level_surface.get_rect(topleft=(self.SCREEN_WIDTH//4, self.SCREEN_HEIGHT/2 - ((self.Y_BLOCKS/2)*self.grid.block_distance) + 100+60)))
        self.screen.blit(next_block_surface, next_block_surface.get_rect(topleft=(self.SCREEN_WIDTH/(4/3), self.SCREEN_HEIGHT/2 - ((self.Y_BLOCKS/2)*self.grid.block_distance) + 100)))  

        self.draw_lock_delay_bar(
            (int(self.SCREEN_WIDTH // 4), int(self.SCREEN_HEIGHT//2*(1/self.scale_factor))),
            (255, 40, 20),
            self.drop_collision_timer,
            self.LOCK_DELAY_MS
        )

        self.draw_lock_delay_bar(
            (int(self.SCREEN_WIDTH // 4), int(self.SCREEN_HEIGHT//2*(1/self.scale_factor)-(200*self.scale_factor))),
            (40, 0, 255),
            self.forced_drop_collision_timer,
            self.MAX_LOCK_DELAY_MS
        )

    def draw_lock_delay_bar(self, LOCK_BAR_POS, LOCK_BAR_COLOR, drop_collision_timer, lock_delay) :
        if drop_collision_timer <= 0:
            return  # don't draw when not grounded

        remaining_ratio = max(0, 1 - (drop_collision_timer / lock_delay))
        bar_width = int(self.LOCK_BAR_WIDTH * remaining_ratio)

        # Background
        bg_rect = pygame.Rect(*LOCK_BAR_POS, self.LOCK_BAR_WIDTH, self.LOCK_BAR_HEIGHT)
        pygame.draw.rect(self.screen, self.LOCK_BAR_BG, bg_rect)

        # Foreground (time remaining)
        fg_rect = pygame.Rect(*LOCK_BAR_POS, bar_width, self.LOCK_BAR_HEIGHT)
        pygame.draw.rect(self.screen, LOCK_BAR_COLOR, fg_rect)

    def game_over(self, database_uploading):

        if not database_uploading == GameState.GAME_OVER_DATABASE_UPLOAD:
            self.game_running()
            self.screen.blit(self.overlay, (0, 0))
            game_over_surface = self.font_title.render("WASTED", True, (255, 0, 0))
            restart_instructions_surface = self.font_ui.render("Press R to restart", True, (255, 255, 255))
            main_menu_instructions_surface = self.font_ui.render("Press M to quit to Main Menu", True, (255, 255, 255))
            leaderboard_instructions_surface = self.font_ui.render("Press L to upload score to Leaderboard", True, (255, 255, 255))
            self.screen.blit(game_over_surface, game_over_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)))
            self.screen.blit(restart_instructions_surface, restart_instructions_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 200)))
            self.screen.blit(main_menu_instructions_surface, main_menu_instructions_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 300)))
            self.screen.blit(leaderboard_instructions_surface, leaderboard_instructions_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 400)))
        else: 
            self.screen.blit(self.overlay, (0, 0))
            prompt_surface = self.font_ui.render("Enter your name:", True, (255, 255, 255))
            name_surface = self.font_ui.render(self.player_name + "_", True, (255, 255, 255))
            prompt_2_surface = self.font_ui.render("Press ENTER to submit your score to the DB:", True, (255, 255, 255))

            self.screen.blit(prompt_surface, (self.SCREEN_WIDTH // 2 - 200, self.SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(name_surface, (self.SCREEN_WIDTH // 2 - 200, self.SCREEN_HEIGHT // 2))
            self.screen.blit(prompt_2_surface, prompt_2_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 150)))

    def game_running_pause(self):
        self.game_running()
        self.screen.blit(self.overlay, (0, 0))
        pause_surface = self.font_title.render("Paused", True, (255, 255, 255))
        resume_instructions_surface = self.font_ui.render("Press R to Resume Game", True, (255, 255, 255))
        quit_instructions_surface = self.font_ui.render("Press M to go to Main Menu", True, (255, 255, 255))
        self.screen.blit(pause_surface, pause_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)))
        self.screen.blit(resume_instructions_surface, resume_instructions_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 200)))
        self.screen.blit(quit_instructions_surface, quit_instructions_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 400)))

    def advance_level(self):
        self.level += 1
        self.level_duration_ms = self.TOTAL_LEVEL_DURATION_MS + (3_000*self.level)
        self.DROP_INTERVAL_MS *= 0.95
        self.LOCK_DELAY_MS *= 0.95
        self.MAX_LOCK_DELAY_MS *= 0.95

        return self.level, self.TOTAL_LEVEL_DURATION_MS, self.level_duration_ms, self.DROP_INTERVAL_MS, self.LOCK_DELAY_MS, self.MAX_LOCK_DELAY_MS

    def timer(self):
        self.level_duration_ms -= self.dt
        seconds_left = max(0, (self.level_duration_ms - self.level_time_ms) // 1000)
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        self.timer_text = f"{minutes}:{seconds:02d}"

        return self.level_duration_ms, self.timer_text

    def reset_game(self):
        self.archived_blocks = []
        self.points = 0
        self.level = 1
        
        self.is_active_block = False

        self.grid = Grid(self.X_BLOCKS, self.Y_BLOCKS, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.GRID_BLOCK_SIZE)
        self.current_grid = self.grid.grid

        self.level_duration_ms = self.TOTAL_LEVEL_DURATION_MS
        self.DROP_INTERVAL_MS = 750
        self.drop_timer = 0
        self.drop_collision_timer = 0
        self.forced_drop_collision_timer = 0

        self.sound.play_music()

        return (self.is_active_block,
            self.archived_blocks,
            self.points,
            self.level,
            self.grid,
            self.current_grid,
            self.level_duration_ms,
            self.DROP_INTERVAL_MS,
            self.drop_timer,
            self.drop_collision_timer,
            self.forced_drop_collision_timer
        )

    def create_block(self):
        if not self.next_block:
            selected_block = self.blocks.select_block()
            self.next_block = self.blocks.select_block()
            self.block = Block(selected_block)
            self.shadow_block = Block(selected_block)
        else:
            selected_block = self.next_block
            self.next_block = self.blocks.select_block()
            self.block = Block(selected_block)
            self.shadow_block = Block(selected_block)

        return self.block, self.shadow_block, self.next_block

    def check_game_over(self):
        block_is_creatable = self.block.check_block_creation(self.archived_blocks)
        if not block_is_creatable:
            is_active_block = False
            self.game_state = self.game_state.GAME_OVER
            self.sound.play_game_over()
        else:
            is_active_block = True

        return is_active_block, self.game_state

    def check_main_menu_option_selected(self, mouse_pos):

        self.game_state = self.game_state.MAIN_MENU

        if self.start_game_menu_option.rect.collidepoint(mouse_pos):
            self.game_state = self.game_state.MAIN_GAME

        elif self.leaderboard_menu_option.rect.collidepoint(mouse_pos):
            self.game_state = self.game_state.LEADERBOARD

        elif self.quit_game_menu_option.rect.collidepoint(mouse_pos):
            pygame.quit()
            quit()

        elif self.ultrawide_menu_option.rect.collidepoint(mouse_pos):
            self.scale_factor = 1
            self.rebuild_scaled_assets()

        elif self.laptop_menu_option.rect.collidepoint(mouse_pos):
            self.scale_factor = 0.6
            self.rebuild_scaled_assets()
        return self.game_state
    
    def end_current_block_and_clear_rows(self):
    
        self.is_active_block = False

        self.archived_blocks.append(self.block)
        self.archived_blocks = [b for b in self.archived_blocks if b.block_coords]

        rows_cleared = self.grid.clear_rows(self.current_grid, self.archived_blocks)
        self.grid.move_rows(self.current_grid, self.archived_blocks)

        self.points += int(rows_cleared * (1 + (self.level / 10)) * 1000)
        self.drop_collision_timer = 0
        self.forced_drop_collision_timer = 0
        self.collision_reached = False

        return self.is_active_block, self.archived_blocks, self.points, self.drop_collision_timer, self.forced_drop_collision_timer, self.collision_reached

    def rebuild_scaled_assets(self):
        """
        Rebuild everything that depends on self.scale_factor.
        Call this AFTER changing self.scale_factor and screen dimensions.
        """

        # --- Scaled dimensions ---
        self.GRID_BLOCK_SIZE = int(50 * self.scale_factor)

        self.LOCK_BAR_WIDTH  = int(200 * self.scale_factor)
        self.LOCK_BAR_HEIGHT = int(12 * self.scale_factor)

        # --- Overlay ---
        self.overlay = pygame.Surface(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        self.overlay.fill((0, 0, 0, self.OVERLAY_ALPHA))

        # --- Fonts ---
        self.font_title = pygame.font.SysFont(
            "Arial", int(90 * self.scale_factor)
        )
        self.font_ui = pygame.font.SysFont(
            "Arial", int(45 * self.scale_factor)
        )

        # --- Text surfaces ---
        self.tetris_surface = self.font_title.render(
            "Tetris", True, (255, 255, 255)
        )

        # --- Background ---
        self.background = pygame.image.load(self.background_path)
        self.background_rect = self.background.get_rect()
        self.background_rect.center = (
            self.SCREEN_WIDTH // 2,
            self.SCREEN_HEIGHT // 2
        )

        # --- Logos ---
        self.logo = pygame.image.load(self.logo_path)
        self.logo = pygame.transform.scale_by(self.logo, self.scale_factor)
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.center = (
            self.SCREEN_WIDTH // 2,
            int(150 * self.scale_factor)
        )

        self.main_menu_logo = pygame.image.load(self.main_menu_logo_path)
        self.main_menu_logo = pygame.transform.scale_by(
            self.main_menu_logo, self.scale_factor
        )
        self.main_menu_logo_rect = self.main_menu_logo.get_rect()
        self.main_menu_logo_rect.center = (
            self.SCREEN_WIDTH // 2,
            int(200 * self.scale_factor)
        )

        # --- Buttons ---
        self.start_game_menu_option = Button(
            self.screen,
            "Start Game",
            (self.SCREEN_WIDTH // 2, int(600 * self.scale_factor))
        )
        self.leaderboard_menu_option = Button(
            self.screen,
            "LeaderBoard",
            (self.SCREEN_WIDTH // 2, int(800 * self.scale_factor))
        )
        self.quit_game_menu_option = Button(
            self.screen,
            "Quit Game",
            (self.SCREEN_WIDTH // 2, int(1000 * self.scale_factor))
        )
        self.ultrawide_menu_option = Button(
            self.screen,
            "Ultrawide Res",
            (self.SCREEN_WIDTH // 2 - 200, int(1200 * self.scale_factor))
        )
        self.laptop_menu_option = Button(
            self.screen,
            "Laptop Res",
            (self.SCREEN_WIDTH // 2 + 200, int(1200 * self.scale_factor))
        )

        # --- Grids (depend on block size & screen size) ---
        self.grid = Grid(
            self.X_BLOCKS,
            self.Y_BLOCKS,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.GRID_BLOCK_SIZE
        )
        self.next_block_grid = Next_Block_Grid(
            8, 3,
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.GRID_BLOCK_SIZE
        )

        self.current_grid = self.grid.grid
