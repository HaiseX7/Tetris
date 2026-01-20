# Example file showing a basic pygame "game loop"
import pygame
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from Game import Game
from GameState import GameState

# =========================
# GAME STATE FUNCTIONS
# =========================

game = Game()

# =========================
# SUPABASE
# =========================

def submit_score(username: str, score: int):
    # Don't send created_at; let the DB set it.
    supabase.table("Score_Fact").insert({
        "Username": username,
        "Score": score
    }).execute()

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

resp = (
        supabase
        .table("Score_Fact")
        .select("Username,Score,Datetime")
        .order("Score", desc=True)
        .order("Datetime", desc=True)   # tie-breaker
        .limit(10)
        .execute()
)

# =========================
# GAME LOOP
# =========================

while game.running:

    game.dt = game.clock.tick(60) 

    if game.game_state == GameState.MAIN_GAME:
        # Clock Ticking
        game.level_duration_ms, game.timer_text = game.timer()
        # Level Maintenance
        if game.level_duration_ms <= 0:
            game.level, game.TOTAL_LEVEL_DURATION_MS, game.level_duration_ms, game.DROP_INTERVAL_MS, game.LOCK_DELAY_MS, game.MAX_LOCK_DELAY_MS = game.advance_level()

    # Block Creation Logic. If a block is not creatable then its Game over.
    if not game.is_active_block and game.game_state == GameState.MAIN_GAME:
        game.block, game.shadow_block, game.next_block = game.create_block()
        game.is_active_block, game.game_state = game.check_game_over()

    # Event Logic.
    change_game_state = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game.game_state == GameState.MAIN_GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_LEFT:
                    valid_move = game.block.check_collisions(game.current_grid, game.archived_blocks, 0, -1)
                    if valid_move:    
                        game.block.move_left()
                        game.sound.play_click()
                        game.drop_collision_timer = 0
                if event.key == pygame.K_RIGHT:
                    valid_move = game.block.check_collisions(game.current_grid, game.archived_blocks, 0, 1)
                    if valid_move:
                        game.block.move_right()
                        game.sound.play_click()
                        game.drop_collision_timer = 0
                if event.key == pygame.K_DOWN:
                    valid_move = game.block.check_collisions(game.current_grid, game.archived_blocks, 1, 0)
                    if valid_move:
                        game.drop_time = 0
                        game.block.move_down(shadow=False)
                        game.sound.play_click()
                        drop_collision_timer = 0
                if event.key == pygame.K_d:
                    valid_move = True
                    while valid_move:
                        valid_move = game.block.check_collisions(game.current_grid, game.archived_blocks, 1, 0)
                        if valid_move:
                            game.drop_time = 0
                            game.block.move_down(shadow=False)
                            game.sound.play_click()
                            game.drop_collision_timer = 0
                    game.drop_collision_timer+=(game.LOCK_DELAY_MS//2)
                if event.key == pygame.K_UP:
                    new_coords = game.block.rotate()
                    valid_move = game.block.check_rotate_collisions(game.current_grid, game.archived_blocks, new_coords)
                    if valid_move:
                        game.block.block_coords = new_coords
                        game.sound.play_click()
                        game.drop_collision_timer = 0
                    else:
                        game.drop_collision_timer = game.block.try_kick_rotate(game.current_grid, game.archived_blocks, game.sound, game.drop_collision_timer)
                if event.key == pygame.K_p:
                    game.game_state = GameState.MAIN_GAME_PAUSED
        if game.game_state == GameState.MAIN_GAME_PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.game_state = GameState.MAIN_GAME
                if event.key == pygame.K_m:          
                    game.is_active_block, game.archived_blocks, game.points, game.level, game.grid, game.current_grid, game.level_duration_ms, game.DROP_INTERVAL_MS, game.drop_timer, game.drop_collision_timer, game.forced_drop_collision_timer = game.reset_game()
                    game.game_state = GameState.MAIN_MENU
        if game.game_state == GameState.GAME_OVER:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.is_active_block, game.archived_blocks, game.points, game.level, game.grid, game.current_grid, game.level_duration_ms, game.DROP_INTERVAL_MS, game.drop_timer, game.drop_collision_timer, game.forced_drop_collision_timer = game.reset_game()
                    game.game_state = GameState.MAIN_GAME
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_l:
                    game.game_state = GameState.GAME_OVER_DATABASE_UPLOAD
                    game.entering_name = True
                if event.key == pygame.K_m:
                    game.is_active_block, game.archived_blocks, game.points, game.level, game.grid, game.current_grid, game.level_duration_ms, game.DROP_INTERVAL_MS, game.drop_timer, game.drop_collision_timer, game.forced_drop_collision_timer = game.reset_game()
                    game.game_state = GameState.MAIN_MENU
        if game.game_state == GameState.GAME_OVER_DATABASE_UPLOAD:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
            if game.entering_name and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game.entering_name = False  # done typing
                        game.game_state = GameState.GAME_OVER
                        submit_score(game.player_name, game.points)
                    elif event.key == pygame.K_BACKSPACE:
                        game.player_name = game.player_name[:-1]
                    else:
                        if len(game.player_name) < game.MAX_NAME_LEN:
                            if event.unicode.isprintable():
                                game.player_name += event.unicode
        if game.game_state == GameState.MAIN_MENU:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit() 
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                game.game_state = game.check_main_menu_option_selected(mouse_pos)
                if not game.game_state == GameState.MAIN_MENU:
                    change_game_state = True
        if game.game_state == GameState.LEADERBOARD:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_m:
                    game.game_state = GameState.MAIN_MENU
                if event.key == pygame.K_r:
                    resp = (
                        supabase
                        .table("Score_Fact")
                        .select("Username,Score,Datetime")
                        .order("Score", desc=True)
                        .order("Datetime", desc=True)   # tie-breaker
                        .limit(10)
                        .execute()
                    )
    # If the game state changes we want to start the entire loop over so that variables initialize properly before being referenced.
    if change_game_state:
        continue

    # Gravity Dropping
    if game.game_state == GameState.MAIN_GAME:
        game.drop_timer += game.dt
        if game.drop_timer >= game.DROP_INTERVAL_MS:
            game.drop_timer -= game.DROP_INTERVAL_MS
            if game.block.check_collisions(game.current_grid, game.archived_blocks, 1, 0):
                game.block.move_down(shadow=False)

        # Lock delay (soft + hard cap)
        grounded = not game.block.check_collisions(game.current_grid, game.archived_blocks, 1, 0)
        if grounded:
            game.drop_collision_timer += game.dt
            game.forced_drop_collision_timer += game.dt
            if game.drop_collision_timer >= game.LOCK_DELAY_MS or game.forced_drop_collision_timer >= game.MAX_LOCK_DELAY_MS:
                (game.is_active_block,game.archived_blocks,game.points,game.drop_collision_timer,game.forced_drop_collision_timer,game.collision_reached) = game.end_current_block_and_clear_rows()
        else:
            game.drop_collision_timer = 0
            game.collision_reached = False        
    
    # RENDER YOUR GAME HERE
    if game.game_state == GameState.MAIN_MENU:
        game.main_menu()
    else:
        if game.game_state == GameState.MAIN_GAME:
            game.game_running()
        elif game.game_state == GameState.LEADERBOARD:
            game.leaderboard(resp.data)
        elif game.game_state == GameState.GAME_OVER:
            game.game_over(game.game_state)
        elif game.game_state == GameState.GAME_OVER_DATABASE_UPLOAD:
            game.game_over(game.game_state)  
        elif game.game_state == GameState.MAIN_GAME_PAUSED:
            game.game_running_pause() 

    # flip() the display to put your work on screen
    pygame.display.flip()

