import random

class Blocks:
    
    def __init__(self):

        # Reds
        red = (215, 55, 55)
        red_shadow = (249, 155, 155)

        # Blues (deep)
        blue = (40, 70, 195)
        blue_shadow = (147, 171, 243)

        # Yellows
        yellow = (235, 205, 55)
        yellow_shadow = (252, 235, 163)

        # Oranges
        orange = (235, 140, 40)
        orange_shadow = (252, 215, 155)

        # Greens
        green = (50, 185, 85)
        green_shadow = (159, 237, 183)

        # Cyans
        cyan = (45, 205, 215)
        cyan_shadow = (159, 243, 247)

        # Purples (deep)
        purple = (150, 50, 205)
        purple_shadow = (220, 163, 247)

        # I (spawns on the 2nd row of the 4x4 box in SRS)
        self.I = {
            "color": cyan,
            "shadow_color": cyan_shadow,
            "coords": {(3, 1), (4, 1), (5, 1), (6, 1)},
            "pivot": (4.5, 1.5)
        }

        # O (2x2 in the top center)
        self.square = {
            "color": yellow,
            "shadow_color": yellow_shadow,
            "coords": {(4, 0), (5, 0), (4, 1), (5, 1)},
            "pivot": (4.5, 0.5)  # <-- correct center of the 2x2
        }

        # J (flat with the nub on the left)
        self.J = {
            "color": blue,
            "shadow_color": blue_shadow,
            "coords": {(3, 0), (3, 1), (4, 1), (5, 1)},
            "pivot": (4, 1)
        }

        # L (flat with the nub on the right)
        self.L = {
            "color": orange,
            "shadow_color": orange_shadow,
            "coords": {(5, 0), (3, 1), (4, 1), (5, 1)},
            "pivot": (4, 1)
        }

        # S (top row on right, bottom row on left)
        self.S = {
            "color": green,
            "shadow_color": green_shadow,
            "coords": {(4, 0), (5, 0), (3, 1), (4, 1)},
            "pivot": (4, 1)
        }

        # Z (top row on left, bottom row on right)
        self.Z = {
            "color": red,
            "shadow_color": red_shadow,
            "coords": {(3, 0), (4, 0), (4, 1), (5, 1)},
            "pivot": (4, 1)
        }

        # T (flat with stem down)
        self.T = {
            "color": purple,
            "shadow_color": purple_shadow,
            "coords": {(4, 0), (3, 1), (4, 1), (5, 1)},
            "pivot": (4, 1)
        }

        self.shapes = [self.I, self.square, self.J, self.L, self.Z, self.S, self.T]
        self.batch = []
        #self.shapes = [self.shape_2]

    def generate_batch(self):
        possibilites = list(range(len(self.shapes)))
        batch = []
        while possibilites:
            choice = random.choice(possibilites)
            possibilites.remove(choice)
            batch.append(choice)
        return batch

    def select_block(self):
        if self.batch:
            selected_block = self.shapes[self.batch[0]]
            self.batch.remove(self.batch[0])
        else:
            self.batch = self.generate_batch()
            selected_block = self.shapes[self.batch[0]]
            self.batch.remove(self.batch[0])
            
        return selected_block
 