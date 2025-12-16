import math
import time
import pygame as pg
from consts import *


class Draw:

    def draw_loading(self):
        ip_text = self.font.render("".join(("IP: ", *self.input_host)), True, "white")
        x = self.width // 2 - ip_text.get_width() // 2
        y = self.height * 3 // 8 - ip_text.get_height() // 2
        self.screen.blit(ip_text, (x, y))
        if (time.time() * 2) % 2 < 1:
            pg.draw.line(self.screen, "white",
                (x + ip_text.get_width(), y + ip_text.get_height() // 6),
                (x + ip_text.get_width(), y + ip_text.get_height() * 5 // 6),
            )

        if self.ready:
            loading_str = f"Waiting for opponent{'.' * (int(time.time() * 2) % 4)}"
            loading_text = self.font.render(loading_str, True, "white")
            self.screen.blit(loading_text, (
                self.width // 2 - loading_text.get_width() // 2,
                self.height * 5 // 8 - loading_text.get_height() // 2
            ))


    def load_assets(self):
        self.bg_img = pg.image.load("assets/bg.jpg")
        self.bg_img.fill((192, 160, 128), (0, 0, *self.bg_img.get_size()), pg.BLEND_MULT)
        self.board_img = pg.image.load("assets/board.png")
        self.light_img = pg.image.load("assets/light.svg")
        self.dark_img = pg.image.load("assets/dark.svg")
        self.waiting_img = pg.image.load("assets/waiting.svg")
        self.arrow_imgs = pg.image.load("assets/arrows.png")
        self.move_sound = pg.mixer.Sound("assets/move.wav")
        self.roll_sound = pg.mixer.Sound("assets/roll.wav")

        self.bg_img = self.bg_img.convert()
        self.board_img = self.board_img.convert_alpha()
        self.light_img = self.light_img.convert_alpha()
        self.dark_img = self.dark_img.convert_alpha()
        self.waiting_img = self.waiting_img.convert_alpha()
        self.arrow_imgs = self.arrow_imgs.convert_alpha()
        self.move_sound.set_volume(0.5)
        self.roll_sound.set_volume(0.5)


    def render_score(self):
        score_text = self.font.render("Score", True, "white")
        self.score_pos = (
            self.width // 2 - score_text.get_width() // 2,
            self.tile_size // 2
        )

        rect = (0, self.score_pos[1], self.width, score_text.get_height())
        dark = pg.surface.Surface(rect[2:4])
        dark.fill((128, 128, 128))
        self.bg_img.blit(dark, rect[0:2], special_flags=pg.BLEND_MULT)
        self.bg_img.blit(score_text, self.score_pos)


    def render_player_labels(self):
        self.you_text = self.font.render("You", True, "white")
        self.opponent_text = self.font.render("Them", True, "white")

        color = 0x88FF22
        # color = 0xFF3311

        self.highlight_you_text = self.you_text.copy()
        self.highlight_opponent_text = self.opponent_text.copy()
        self.highlight_you_text.fill(
            color, special_flags=pg.BLEND_MULT
        )
        self.highlight_opponent_text.fill(
            color, special_flags=pg.BLEND_MULT
        )


    def blit_player_labels(self):
        you_size = self.you_text.get_size()
        opponent_size = self.opponent_text.get_size()

        center = (self.width // 6, self.height - self.tile_size * 3)

        self.you_pos = (
            center[0] - you_size[0] // 2,
            center[1] - you_size[1] // 2
        )
        self.opponent_pos = (
            self.width - center[0] - opponent_size[0] // 2,
            center[1] - opponent_size[1] // 2
        )

        if self.color == DARK:
            self.you_pos = (
                self.width - self.you_pos[0] - you_size[0], self.you_pos[1]
            )
            self.opponent_pos = (
                self.width - self.opponent_pos[0] - opponent_size[0], self.opponent_pos[1]
            )

        self.bg_img.blit(self.you_text, self.you_pos)
        self.bg_img.blit(self.opponent_text, self.opponent_pos)


    def render_bg(self):
        self.render_score()
        self.render_player_labels()
        self.blit_player_labels()
        
        finish_text = self.font.render("Done", True, "white")
        finish_pos = (
            self.finish_rect[0] + self.finish_rect[2] // 2 - finish_text.get_width() // 2,
            self.finish_rect[1] + self.finish_rect[3] // 2 - finish_text.get_height() // 2
        )

        bg_color = 0xA89039
        border_color = 0x84810D
        padding = 6
        light_piece_rect = (
            self.light_piece_rect[0] - padding,
            self.light_piece_rect[1] - padding,
            self.light_piece_rect[2] + padding * 2,
            self.light_piece_rect[3] + padding * 2
        )
        dark_piece_rect = (
            self.dark_piece_rect[0] - padding,
            self.dark_piece_rect[1] - padding,
            self.dark_piece_rect[2] + padding * 2,
            self.dark_piece_rect[3] + padding * 2
        )
        pg.draw.rect(self.bg_img, bg_color, self.dice_rect)
        pg.draw.rect(self.bg_img, bg_color, light_piece_rect)
        pg.draw.rect(self.bg_img, bg_color, dark_piece_rect)
        pg.draw.rect(self.bg_img, bg_color, self.finish_rect)

        pg.draw.rect(self.bg_img, border_color, self.dice_rect, 2)
        pg.draw.rect(self.bg_img, border_color, light_piece_rect, 2)
        pg.draw.rect(self.bg_img, border_color, dark_piece_rect, 2)
        pg.draw.rect(self.bg_img, border_color, self.finish_rect, 2)

        self.bg_img.blit(finish_text, finish_pos)


    def draw_board(self):
        w = 3
        h = 8
        self.board_surf.blit(self.board_img, (0, 0))

        for i in range(w):
            for j in range(h):
                curr_piece = self.board[i + j * w]
                if curr_piece == OUTSIDE:
                    continue

                pos = (
                    i * self.tile_size + self.tile_size // 2 - self.piece_radius,
                    j * self.tile_size + self.tile_size // 2 - self.piece_radius,
                )

                if curr_piece == LIGHT:
                    self.board_surf.blit(self.light_img, pos)
                elif curr_piece == DARK:
                    self.board_surf.blit(self.dark_img, pos)


    def draw_move(self):
        if self.move is None or sum(self.dice) == 0: return
        steps = self.get_next_steps()

        for i in range(len(steps)):
            idx = steps[i]
            color = 1
            x = int(((idx %  3)) * self.tile_size) + self.board_rect[0]
            y = int(((idx // 3)) * self.tile_size) + self.board_rect[1]
            
            if i == len(steps) - 1:
                diff = idx - steps[i - 1]
                arrow_type = "end"
            elif i == 0:
                if self.move == -1:
                    arrow_type = "middle"
                else:
                    arrow_type = "start"
                diff = steps[i + 1] - idx
            else:
                diff1 = idx - steps[i - 1]
                diff2 = steps[i + 1] - idx

                if diff1 == diff2:
                    arrow_type = "middle"
                    diff = abs(diff1)

                else:
                    arrow_type = "bend"
                    diff = diff2 if self.color == LIGHT else diff1
                    if self.color == DARK:
                        color = -1

            if diff == ( 1 * color): d = "east"
            elif diff == (-1 * color): d = "west"
            elif diff == ( 3 * color): d = "south"
            else: d = "north"

            arrow_types = ["start", "middle", "bend", "end"]
            directions = ["north", "east", "south", "west"]

            dx = arrow_types.index(arrow_type) * self.tile_size
            dy = directions.index(d) * self.tile_size

            self.screen.blit(self.arrow_imgs, (x, y), (dx, dy, self.tile_size, self.tile_size))


    def draw_die(self, x, y, lights: set):
        r = self.piece_radius
        points = [(
            x + math.cos(i / 3 * math.tau) * r,
            y + math.sin(i / 3 * math.tau) * r
        ) for i in range(3)]
        pg.draw.polygon(self.screen, DARK_COLOR, points)
        for p in points:
            pg.draw.line(self.screen, "black", (x, y), p, 2)

        points.append((x, y))

        for i in range(4):
            if i in lights:
                color = "white"
            else:
                color = "black"

            pg.draw.circle(self.screen, color, points[i], self.piece_radius / 4)


    def draw_dice(self):
        for i in range(4):
            if self.dice[i]:
                dice_set = {3}
            else:
                dice_set = set()
            
            x = i % 2
            y = i // 2
            self.draw_die(
                self.dice_rect[0] + self.dice_rect[2] * (x * 2 + 1) // 4,    
                self.dice_rect[1] + self.dice_rect[3] * (y * 2 + 1) // 4,    
            dice_set)


    def draw_ui(self):
        def draw_pieces(npieces, color, rect):
            for i in range(npieces):
                offset_x = self.piece_radius * (self.piece_spacing_factor * i)
                if color == LIGHT:
                    x = rect[0] + offset_x
                else:
                    x = rect[0] + rect[2] - offset_x - self.dark_img.get_width()
                pos = (x, rect[1])

                if color == LIGHT:
                    self.screen.blit(self.light_img, pos)
                else:
                    self.screen.blit(self.dark_img, pos)

        draw_pieces(self.light_pieces, LIGHT, self.light_piece_rect)
        draw_pieces(self.dark_pieces, DARK, self.dark_piece_rect)
        # draw_pieces(self.light_score, LIGHT, self.tile_size // 3)
        # draw_pieces(self.dark_score, DARK, self.tile_size // 3)
        light_text = self.font.render(str(self.light_score), True, "white")
        dark_text = self.font.render(str(self.dark_score), True, "white")

        self.screen.blit(light_text, (
            self.width // 4 - light_text.get_width() // 2,
            self.score_pos[1]
        ))
        self.screen.blit(dark_text, (
            self.width // 4 * 3 - dark_text.get_width() // 2,
            self.score_pos[1]
        ))

        if self.my_turn:
            if int(time.time() * 2) & 1:
                self.screen.blit(
                    self.highlight_you_text,
                    self.you_pos,
                )
        else:
            angle = -int(time.monotonic() * 8 % 8) / 8 * 360
            text_size = self.opponent_text.get_size()
            img = pg.transform.rotate(self.waiting_img, angle)
            x = self.opponent_pos[0] + text_size[0] // 2 - img.get_width() / 2
            y = self.opponent_pos[1] + text_size[1] * 3 // 2 - img.get_height() // 2
            self.screen.blit(img, (x, y))

        self.draw_dice()
        self.draw_move()
