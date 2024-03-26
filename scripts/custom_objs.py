import pygame

from .devfw.elems import Element

'''
defining tetromino using the following grid:
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15

defining them as a list using the above numbers
example of T block:

T.shape = [1, 4, 5, 6]
'''
class Tetrimino(Element):
  shapes : dict = {
    'L':[[0, 1, 2, 4], [0, 1, 5, 9], [2, 4, 5, 6], [0, 4, 8, 9]],
    'J':[[0, 4, 5, 6], [0, 1, 4, 8], [0, 1, 2, 6], [1, 5, 8, 9]],
    'O':[[0, 1, 4, 5]],
    'I':[[0, 1, 2, 3], [0, 4, 8, 12]],
    'S':[[1, 2, 4, 5], [0, 4, 5, 9]],
    'Z':[[0, 1, 5, 6], [1, 4, 5, 8]],
    'T':[[1, 4, 5, 6], [0, 4, 5, 8], [0, 1, 2, 5], [1, 4, 5, 9]]
  }

  shape_colors : dict = {
    'L':(255, 127, 0),
    'J':(0, 0, 255),
    'O':(255, 255, 0),
    'I':(0, 255, 255),
    'S':(0, 255, 0),
    'Z':(255, 0, 0),
    'T':(128, 0, 128)
  }

  faded_shape_colors : dict = {
    'L':(63, 31, 0),
    'J':(0, 0, 63),
    'O':(63, 63, 0),
    'I':(0, 63, 63),
    'S':(0, 63, 0),
    'Z':(63, 0, 0),
    'T':(31, 0, 31)
  }

  def __init__(self, shape:str):
    super().__init__()

    self.shape_type : str = shape
    self.rot_ind    : int = 0
    self.pos        : pygame.Vector2 = pygame.Vector2(4, 0)
    self.dims       : tuple = self.get_size()

  # returns the list representation of the tetrimino as defined above
  @property
  def shape(self) -> list:
    return Tetrimino.shapes[self.shape_type][self.rot_ind].copy()

  # returns all coordinates occupied by this tetrimino on the field (modified by position)
  @property
  def field_coords(self) -> list:
    coordinates = []
    for i in range(4):
      for j in range(4):
        if self.valid_cell(i, j):
          coordinates.append([int(self.pos.x + i), int(self.pos.y + j)])
    return coordinates

  # returns the size of the tetrimino based on the representation
  def get_size(self) -> tuple:
    width  = 0
    height = 0
    for i in range(4):
      for j in range(4):
        if self.valid_cell(i, j):
          width  = max(i, width)
          height = max(j, height)
    width += 1
    height += 1
    return width, height

  # rotates the tetrimino
  def rotate(self, direction:int) -> None:
    self.rot_ind = (self.rot_ind + direction) % len(Tetrimino.shapes[self.shape_type])
    self.dims = self.get_size()

  # renders the tetrimino based on given field coordinates and the tetrimino's current pos
  def field_render(self, surf:pygame.Surface, field_tl:tuple, cell_size:int, faded:bool=False) -> None:
    fx, fy = field_tl
    for i in range(4):
      for j in range(4):
        if self.valid_cell(i, j):
          color = Tetrimino.shape_colors[self.shape_type] if not faded else Tetrimino.faded_shape_colors[self.shape_type]
          pygame.draw.rect(surf, color, (fx + (i + self.pos.x) * cell_size, fy + (j + self.pos.y) * cell_size, cell_size, cell_size))

  # renders the tetrimino on the given surf
  def basic_render(self, surf:pygame.Surface, topleft:tuple, cell_size:int) -> None:
    x, y = topleft
    for i in range(4):
      for j in range(4):
        if self.valid_cell(i, j):
          pygame.draw.rect(surf, Tetrimino.shape_colors[self.shape_type], (x + i * cell_size, y + j * cell_size, cell_size, cell_size))

  # helper to check for the cell positions in the shape
  def valid_cell(self, mat_i:int, mat_j:int) -> bool:
    return mat_i * 4 + mat_j in self.shape

  # moves the tetrimino
  def move(self, x:int, y:int) -> None:
    self.pos.x += x
    self.pos.y += y

  # clamps the tetrimino to the given field dimensions
  def field_clamp(self, min_x:int, min_y:int, max_x:int, max_y:int) -> None:
    width, height = self.dims

    if self.pos.x < min_x:
      self.pos.x = min_x
    if self.pos.y < min_y:
      self.pos.y = min_y

    if self.pos.x + width - 1 > max_x:
      self.pos.x = max_x - width + 1
    if self.pos.y + height - 1 > max_y:
      self.pos.y = max_y - height + 1

  # dual purpose function, either returns a copy of self or copies other into self
  def copy(self, tetrimino:'Tetrimino'=None) -> 'Tetrimino':
    if tetrimino == None:
      t = Tetrimino(self.shape_type)
      t.pos = self.pos.copy()
      t.rot_ind = self.rot_ind
      t.dims = self.get_size()
      return t

    self.shape_type = tetrimino.shape_type
    self.pos.update(tetrimino.pos)
    self.rot_ind = tetrimino.rot_ind
    self.dims = self.get_size()
    return self

  # resets the tetrimino to base rotation, at the top of screen, can take a shape type for initialization
  def reset(self, shape_type:str=None) -> None:
    self.shape_type = shape_type if shape_type else self.shape_type
    self.pos = pygame.Vector2(4, 0)
    self.rot_ind = 0
    self.dims = self.get_size()