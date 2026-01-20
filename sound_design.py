import os
import pygame

class SoundDesign:

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.music_path = os.path.join(self.BASE_DIR, 'Tetris.mp3')
        self.click_path = os.path.join(self.BASE_DIR, 'Tetris_Click.mp3')
        self.go_path = os.path.join(self.BASE_DIR, 'Tetris_Game_Over.mp3')

    def play_music(self):
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(self.music_path), -1)

    def play_click(self):
        pygame.mixer.Channel(1).play(pygame.mixer.Sound(self.click_path))

    def play_game_over(self):
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(self.go_path))