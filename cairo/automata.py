import cairo
import argparse
import numpy as np
from scipy.signal import convolve
from render_automata import Renderer
from color_interpolation import hex2rgb
from gi.repository import Gtk, GLib

colors = ['FFFFFF', '00000', 'F24236', '0165a9', 'EDA10E', 'ee3037', '006AFF', 'FFFFFF']
colors = [hex2rgb(h) for h in colors]


class Automata(Renderer):
    def __init__(self, width, height, grid,  gtk, animate, frames):
        self.gtk_mode = gtk
        self.matrix = cairo.Matrix(width, 0, 0, height, 0, 0)
        # self.matrix = cairo.Matrix(width / 2, 0, 0, -height / 2, width / 2, height / 2)

        self.box_number = (grid, grid)
        self.box_size = (width/self.box_number[0], height/self.box_number[1])
        self.norm_box_size = (1/self.box_number[0], 1/self.box_number[1])
        self.lw = 1e-3
        self.lc = colors[1]

        self.M = np.zeros(self.box_number, dtype=np.bool)
        self.kernel = np.ones((3, 3))
        self.kernel[1][1] = 0
        super().__init__(width, height, gtk, animate, frames)

    def normalize_mouse(self, x, y):
        return x / self.width,  y / self.height

    def normalize_coord(self, x, y):
        return (self.box_size[0] * x) / self.width, (self.box_size[1] * y) / self.height

    def button_release_receiver(self, wd, event):
        mx, my = self.normalize_mouse(*event.get_coords())
        x, y = int(self.box_number[0]*mx), int(self.box_number[1]*my)
        self.M[x][y] = ~self.M[x][y]

        self.darea.queue_draw()

    def calculate_next_gen(self, wd, event):
        # Make a 2d convolution, with a kernel :
        # 1 1 1
        # 1 0 1
        # 1 1 1
        # This kernel will count the neighbours for each element of the grid
        # Remember that convolution in (image processing) is not a dot product, instead a element-wise multiplication
        # between a subspace of the matrix and the kernel, then all the multiplied elements are sum up.

        ## Rules of Conway's game of life
        # Rule 1: Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        # Rule 2: Any live cell with two or three live neighbours lives on to the next generation.
        # Rule 3: Any live cell with more than three live neighbours dies, as if by overpopulation.
        # Rule 4: Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        neighbours = convolve(self.M, self.kernel, mode='same').flatten() # Number of active neighbours as 1D array
        neighbours = neighbours.flatten()
        for i, n in enumerate(neighbours):
            r = i // self.box_number[0]
            c = i % self.box_number[1]
            if self.M[r][c]:  # A Cell is alive
                if n < 2 or n > 3:  # Rule 1 and 3, For Rule  2 do nothing
                    self.M[r][c] = False
            elif n == 3:  # Rule 4
                self.M[r][c] = True

        self.darea.queue_draw()

    def draw_squares(self, cr: cairo.Context, color=colors[2]):
        cr.set_line_width(self.lw)
        cr.set_source_rgba(*self.lc)
        nx, ny = self.normalize_coord(*np.where(self.M))
        for x, y in zip(nx, ny):
            nx, ny = self.normalize_coord(x, y)
            cr.rectangle(x, y, self.norm_box_size[0], self.norm_box_size[1])
        cr.stroke_preserve()
        cr.set_source_rgba(*color)
        cr.fill()

    def draw_line_grid(self, cr: cairo.Context):
        cr.set_source_rgb(*colors[0])
        cr.set_line_width(1e-3)
        for x in range(1, self.box_number[0]):
            nx = (self.box_size[0] * x)/self.width
            cr.move_to(nx, 1)
            cr.line_to(nx, -1)

        for y in range(1, self.box_number[1]):
            ny = (self.box_size[0] * y) / self.height
            cr.move_to(-1, ny)
            cr.line_to(1, ny)
        cr.stroke()

    def on_draw(self, wd, cr: cairo.Context):
        cr.identity_matrix()
        cr.set_matrix(self.matrix)
        self.draw_line_grid(cr)

        if np.any(self.M):  # Test if at least on is zero
            self.draw_squares(cr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Automata')
    parser.add_argument('--w', type=int, default=700, help='Level of the triangle')
    parser.add_argument('--h', type=int, default=700, help='Level of the triangle')
    parser.add_argument('--n', type=int, default=30, help='Level of the triangle')
    parser.add_argument('--s', type=int, default=1, help='Initial Scale')
    parser.add_argument('--fr', type=int, default=300, help='Number of frames')
    parser.add_argument('--im', action='store_false', help='Use GTK window')
    parser.add_argument('--an', action='store_true', help='Animate')

    args = parser.parse_args()
    app = Automata(args.w, args.h, args.n, args.im, args.an, args.fr)
    if args.im:
        if args.an:
            GLib.timeout_add(50, app.gtk_move)
        Gtk.main()
