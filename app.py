import queue
import threading
import pygame as pg
from draw import *
from client import *
from consts import *

class App(Draw, Client):

    def __init__(self):
        pg.init()
        pg.font.init()
        self.font = pg.font.Font("assets/Rubik/Rubik.ttf", 48)
        pg.display.set_caption("Royal game of Ur")

        self.width, self.height = self.size = (640, 720)
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.running = True
        self.fps = 24
        # self.bg = 0x443322

        self.bg_img = pg.surface.Surface(self.size)

        self.ready = False
        self.connected = False
        self.input_host = []

        self.init_board()
        self.init_rects()
        self.load_assets()
        # self.render_bg()
        # self.draw_board()

        self.start()


    def post_init(self):
        self.render_bg()
        self.connected = True


    def init_board(self):
        self.dark_pieces = 7
        self.light_pieces = 7
        self.light_score = 0
        self.dark_score = 0
        self.board = [EMPTY] * 3 * 8
        self.board[12] = OUTSIDE
        self.board[14] = OUTSIDE
        self.board[15] = OUTSIDE
        self.board[17] = OUTSIDE
        self.move = None

        self.dice = (0, 1, 0, 1)
        self.my_turn = False
        self.selected_tile = None
        self.has_rolled = True
        self.move = None

        self.tile_size = 64
        self.piece_spacing_factor = 0.75
        self.piece_radius = self.tile_size * 3 / 8
        self.board_surf = pg.surface.Surface(
            (3 * self.tile_size, 8 * self.tile_size),
        flags=pg.SRCALPHA)


    def init_rects(self):
        self.board_rect = (
            int(self.size[0] / 2 - self.board_surf.get_width() / 2),
            int(self.size[1] / 2 - self.board_surf.get_height() / 2 + self.tile_size // 2),
            self.tile_size * 3, self.tile_size * 8
        )
        self.light_piece_rect = (
            self.tile_size // 2,
            self.board_rect[1] + self.tile_size * 4 + self.tile_size // 2 - self.piece_radius,
            (6 * self.piece_spacing_factor + 2) * self.piece_radius, self.piece_radius * 2
        )
        self.dark_piece_rect = (
            self.width - self.light_piece_rect[0] - self.light_piece_rect[2],
            *self.light_piece_rect[1:]
        )
        self.dice_rect = (
            self.tile_size // 2, self.board_rect[1],
            int(self.tile_size * 2.5), self.tile_size * 3
        )
        self.finish_rect = (
            self.width - self.dice_rect[0] - self.dice_rect[2], *self.dice_rect[1:]
        )


    def get_next_steps(self, start_square=None):
        nsteps = sum(self.dice)

        if start_square is None:
            start_square = self.move

        if start_square == -1:
            nsteps -= 1

            light_start = 9
            dark_start = 11
            begin = light_start if self.color == LIGHT else dark_start

            start_square = begin

        idx = start_square
        steps = [idx]
        if nsteps <= 0: return steps
        
        for _ in range(nsteps):
            if idx == 0: idx += 1
            elif idx == 2: idx -= 1
            elif idx == 22:
                if self.color == LIGHT:
                    idx -= 1
                else:
                    idx += 1
            elif idx % 3 == 1: idx += 3
            else: idx -= 3
            
            steps.append(idx)

        return steps


    def move_exists(self):
        if sum(self.dice) == 0: return False
        for i in range(len(self.board)):
            if self.board[i] == self.color:
                steps = self.get_next_steps(i)
                if self.validate_move(steps, i): return True

        steps = self.get_next_steps(-1)
        return self.validate_move(steps, -1)


    def validate_move(self, steps, move):
        if sum(self.dice) == 0: return False
        if move != -1:
            if self.board[steps[0]] != self.color: return False
        if self.board[steps[-1]] == self.color: return False
        elif move == -1:
            if self.color == LIGHT and self.light_pieces > 0: return True
            if self.color == DARK and self.dark_pieces > 0: return True
            return False
        if steps[-1] == 10 and self.board[10] != EMPTY: return False

        if steps[0] <= 16: return True
        if steps[-1] >= 15: return True
        
        return False


    def make_move(self):
        if not self.has_rolled or not self.my_turn:
            return
        
        move_exists = self.move_exists()
        last_bit = b"0"

        if self.move is not None:
            steps = self.get_next_steps()
            start_square = steps[0]
            end_square = steps[-1]
            star_tiles = (0, 2, 10, 18, 20)
            last_bit = b"1" if end_square in star_tiles else b"0"
            self.move_sound.play()

            if self.move == -1:
                if self.color == LIGHT:
                    self.light_pieces -= 1
                else:
                    self.dark_pieces -= 1

                self.board[end_square] = self.color
            
            elif end_square in (15, 17):
                self.board[start_square] = EMPTY
                if self.color == LIGHT:
                    self.light_score += 1
                else:
                    self.dark_score += 1

            else:
                self.board[start_square] = EMPTY
                if self.board[end_square] != EMPTY:
                    if self.color == LIGHT:
                        self.dark_pieces += 1
                    else:
                        self.light_pieces += 1

                self.board[end_square] = self.color
        
        elif move_exists:
            return

        self.my_turn = False
        self.selected_tile = None
        self.has_rolled = False
        self.move = None
        self.send_queue.put(b"|".join((b"<move>", self.encode_board() + last_bit)))


    def handle_event(self, event):
        def collide_rect_point(rect, point):
            return (
                rect[0] < point[0] < rect[0] + rect[2] and 
                rect[1] < point[1] < rect[1] + rect[3] 
            )
        
        match event.type:
            case pg.QUIT:
                self.running = False

            case pg.MOUSEBUTTONDOWN:
                board_mouse = collide_rect_point(self.board_rect, event.pos)
                dice_mouse = collide_rect_point(self.dice_rect, event.pos)
                finish_mouse = collide_rect_point(self.finish_rect, event.pos)

                if self.color == LIGHT:
                    piece_mouse = collide_rect_point(self.light_piece_rect, event.pos)
                else:
                    piece_mouse = collide_rect_point(self.dark_piece_rect, event.pos)
                
                if board_mouse and self.my_turn and self.has_rolled:
                    move = (
                        int((event.pos[0] - self.board_rect[0]) / self.tile_size) +
                        int((event.pos[1] - self.board_rect[1]) / self.tile_size) * 3
                    )
                    move_made = False

                    if self.move is not None:
                        steps = self.get_next_steps()
                        if move == steps[-1]:
                            move_made = True
                            self.make_move()
                    if not move_made:
                        self.move = move

                elif dice_mouse and self.my_turn and not self.has_rolled:
                    self.send_queue.put(b"<roll>")
                    self.has_rolled = True

                elif piece_mouse and self.my_turn and self.has_rolled:
                    self.move = -1

                elif finish_mouse:
                    self.make_move()

                if self.move is not None:
                    steps = self.get_next_steps()
                    if not self.validate_move(steps, self.move): self.move = None

            case pg.KEYUP:
                if event.key == pg.K_RETURN:
                    if self.has_rolled:
                        self.make_move()
                    elif self.my_turn:
                        self.send_queue.put(b"<roll>")
                        self.has_rolled = True


    def start(self):
        self.connect_loop()
        self.game_loop()

        pg.quit()


    def connect_loop(self):
        deleting = -1
        deleting_time = 0.33
        
        while not self.connected and self.running:
            while True:
                try:
                    self.handle_message(self.recv_queue.get(False))
                except (queue.Empty, AttributeError):
                    break

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE and len(self.input_host) > 0:
                        deleting = 0

                    elif event.key == pg.K_RETURN and not self.ready:
                        threading.Thread(
                            target=self.init_client,
                            daemon=True,
                        ).start()

                    elif len(self.input_host) < 16 and event.unicode in "0123456789.":
                        self.input_host.append(event.unicode)
                        print("".join(self.input_host))

                elif event.type == pg.KEYUP:
                    if event.key == pg.K_BACKSPACE:
                        deleting = -1
                        if deleting < deleting_time:
                            if len(self.input_host) > 0: self.input_host.pop()

            if deleting >= 0 and deleting < deleting_time:
                deleting += 1 / self.fps
            if deleting >= deleting_time:
                if len(self.input_host) > 0: self.input_host.pop()

            self.screen.blit(self.bg_img, (0, 0))
            self.draw_loading()

            pg.display.flip()
            self.clock.tick(self.fps)


    def game_loop(self):
        while self.running:
            while True:
                try:
                    self.handle_message(self.recv_queue.get(False))
                except queue.Empty:
                    break

            self.screen.blit(self.bg_img, (0, 0))
            
            for event in pg.event.get():
                self.handle_event(event)

            self.draw_board()
            self.screen.blit(self.board_surf, self.board_rect)
            self.draw_ui()

            pg.display.flip()
            self.clock.tick(self.fps)


if __name__ ==  "__main__":
    App()