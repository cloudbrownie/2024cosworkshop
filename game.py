import pygame
import random

from scripts.devfw.elems import Singleton

from scripts.devfw.window import Window
from scripts.devfw.inp    import Input, KeyListener
from scripts.devfw.render import Render, DEFAULT
from scripts.devfw.utils  import bind_func

from scripts.custom_objs import Tetrimino

class Game(Singleton):
  def __init__(self):
    super().__init__()
    self.APP_WIDTH  : int = 800
    self.APP_HEIGHT : int = 800

  def load(self) -> None:
    app_name = 'Game'
    Window(self.APP_WIDTH, self.APP_HEIGHT, app_name)
    Input(app_name)
    Render()

    # set cell sizes
    self.H_CELLS : int = 10
    self.V_CELLS : int = 24
    self.cell_size : int = 30

    # generate 2d field arry
    self.field : list = []
    for i in range(self.V_CELLS):
      self.field.append([])
      for _ in range(self.H_CELLS):
        self.field[i].append((0, 0, 0))

    field_x_pixels = self.H_CELLS * self.cell_size
    field_y_pixels = self.V_CELLS * self.cell_size
    self.field_center     : tuple = self.APP_WIDTH // 2, self.APP_HEIGHT // 2
    self.field_render_ref : tuple = self.field_center[0] - field_x_pixels // 2, self.field_center[1] - field_y_pixels // 2


    self.tetrimino  : Tetrimino = Tetrimino('O')
    self.prev_state : Tetrimino = self.tetrimino.copy()
    self.next_state : Tetrimino = Tetrimino(random.choice(list(Tetrimino.shapes.keys())))

    self.update_delay : float = 0.5
    self.last_update  : float = self.elements['Window'].rt

    self.lock_delay : float = 0.75
    self.lock_start : float = self.elements['Window'].rt


    rotate_right     = bind_func(self.rotate, tetrimino=self.tetrimino, direction=1)
    rotate_left      = bind_func(self.rotate, tetrimino=self.tetrimino, direction=-1)
    move_right       = bind_func(self.move, tetrimino=self.tetrimino, x=1, y=0)
    move_left        = bind_func(self.move, tetrimino=self.tetrimino, x=-1, y=0)
    move_down        = bind_func(self.move, tetrimino=self.tetrimino, x=0, y=1)
    fast_place_piece = bind_func(self.fast_place, self.tetrimino)

    self.elements['Input'].bind_key(pygame.K_d, move_right,   KeyListener.ONPRESS)
    self.elements['Input'].bind_key(pygame.K_a, move_left,    KeyListener.ONPRESS)
    self.elements['Input'].bind_key(pygame.K_s, move_down,    KeyListener.ONPRESS)

    self.elements['Input'].bind_key(pygame.K_SPACE, fast_place_piece, KeyListener.ONPRESS)
    self.elements['Input'].bind_key(pygame.K_p, self.print_field, KeyListener.ONPRESS)

    self.game_over : bool = False

    self.score : int = 0

    self.font : pygame.font.Font = pygame.font.Font('DePixelSchmal.ttf', 50)

  def print_field(self) -> None:
    print()
    for i in range(len(self.field)):
      row_str = ''
      for j in range(len(self.field[i])):
        if self.field[i][j] == (0, 0, 0):
          row_str += '_ '
        else:
          row_str += 'x '
      print(row_str)

  def update(self) -> None:

    # logic --------------------------------------------------------------------
    self.elements['Input'].update()

    # clamp tetrimino
    self.tetrimino.field_clamp(0, 0, self.H_CELLS - 1, self.V_CELLS - 1)

    # play the game
    if not self.game_over:
      self.tetris_loop()

    # rendering ----------------------------------------------------------------

    # default rendering business
    self.elements['Render'].render({DEFAULT:self.elements['Window'].window})
    self.elements['Window'].update()


  def tetris_loop(self) -> None:
    # fix tetrimino position
    if not self.valid_tetrimino_position(self.tetrimino):
      self.tetrimino.copy(self.prev_state)

    # update the tetrimino moving down
    if self.elements['Window'].rt - self.last_update >= self.update_delay:
      self.last_update = self.elements['Window'].rt
      self.tetrimino.move(0, 1)
      if not self.valid_tetrimino_position(self.tetrimino):
        self.tetrimino.move(0, -1)

    # compute projection
    projection = self.project_tetrimino(self.tetrimino)

    # schedule to place block if tetrimino in projection's spot
    if self.tetrimino.pos.y != projection.pos.y:
      self.lock_start = self.elements['Window'].rt

    # place block if
    if self.elements['Window'].rt - self.lock_start >= self.lock_delay:
      self.place(self.tetrimino)

    # queue projection to be drawn onto field as well
    self.elements['Render'].drawf(projection.field_render, self.field_render_ref, self.cell_size, True)

    # save previous tetrimino state
    self.prev_state = self.tetrimino.copy()

  def move(self, tetrimino:Tetrimino, x:int, y:int) -> None:
    if self.game_over:
      return
    tetrimino.move(x, y)
    if not self.valid_tetrimino_position(tetrimino):
      tetrimino.move(-x, -y)

  def rotate(self, tetrimino:Tetrimino, direction:int) -> None:
    if self.game_over:
      return
    tetrimino.rotate(direction)
    if not self.valid_tetrimino_position(tetrimino):
      tetrimino.rotate(-direction)

  # assumes tetrimino is in a valid spot
  def place(self, tetrimino:Tetrimino) -> None:
    if self.game_over:
      return

    for x, y in tetrimino.field_coords:
      self.field[y][x] = Tetrimino.shape_colors[tetrimino.shape_type]
    self.clean_field()

    self.tetrimino.reset(self.next_state.shape_type)
    self.next_state.shape_type = random.choice(list(Tetrimino.shapes.keys()))

    # check if end game
    if not self.valid_tetrimino_position(self.tetrimino):
      self.game_over = True

  def fast_place(self, tetrimino:Tetrimino) -> None:
    self.place(self.project_tetrimino(tetrimino))
    self.clean_field()

  def draw_grid(self, surf:pygame.Surface) -> None:
    for i in range(len(self.field)):
      for j in range(len(self.field[i])):
        rectx = self.field_render_ref[0] + self.cell_size * j
        recty = self.field_render_ref[1] + self.cell_size * i

        if self.field[i][j] != (0, 0, 0):
          pygame.draw.rect(surf, self.field[i][j], (rectx, recty, self.cell_size, self.cell_size))

        pygame.draw.rect(surf, (75, 80, 85), (rectx, recty, self.cell_size, self.cell_size), 1)

  def clean_field(self) -> None:
    cleared = 0
    for i in range(len(self.field)):
      full_row = True
      for j in range(len(self.field[i])):
        if self.field[i][j] == (0, 0, 0):
          full_row = False
          break
      if full_row:
        cleared += 1
        self.field.pop(i)
        self.field.insert(0, [(0, 0, 0) for _ in range(self.H_CELLS)])

    if cleared == 4:
      self.score += 1200
    elif cleared == 3:
      self.score += 300
    elif cleared == 2:
      self.score += 100
    elif cleared == 1:
      self.score += 40

  def valid_tetrimino_position(self, tetrimino:Tetrimino) -> bool:
    for x, y in tetrimino.field_coords:
      if y >= self.V_CELLS or y < 0 or x >= self.H_CELLS or x < 0:
        return False

      if self.field[y][x] != (0, 0, 0):
        return False
    return True

  def project_tetrimino(self, tetrimino:Tetrimino) -> int:
    test = tetrimino.copy()
    for _ in range(self.V_CELLS):
      test.move(0, 1)
      if not self.valid_tetrimino_position(test):
        test.move(0, -1)
        return test
    return 0

  def run(self) -> None:
    self.load()
    self.running : bool = True
    while self.running:
      self.update()
    pygame.quit()

Game().run()