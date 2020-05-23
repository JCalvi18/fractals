import cairo
import argparse
from numpy import pi, cos, exp, linspace, logspace
from renderer import Renderer
from gi.repository import Gtk, GLib
from operator import iconcat
from functools import reduce
from color_interpolation import interpolate, hex2rgb

colors = ['A50104', 'FFB400', '1C5D99', 'F9A03F', '0F8B8D']


class Sier_Arrow(Renderer):
    def __init__(self, width, height, gtk, animate, frames, level):
        self.angle = pi/3  # 60 Degrees
        self.x, self.y = None, None
        self.level = level
        if animate:
            self.on_first_frame = True
            self.length = None
            self.turtle_path = None
            self.delta = self.gen_delta(self.level, frames)
            self.current_level = 1
            self.length = 1 / (2 << (self.current_level - 1)) if self.current_level > 0 else 1
            self.turtle_path = self.generate(self.current_level)
            self.line_color = interpolate(colors[0], colors[1], frames)
        else:
            self.length = 1 / (2 << (self.level - 1)) if self.level > 0 else 1
            self.turtle_path = self.generate(self.level)
            self.current_level = level
            self.delta = None
            self.line_color = hex2rgb(colors[1])

        super().__init__(width, height, gtk, self.delta, frames+90)

    def gen_delta(self, level, n, tail=200):

        space = linspace(0, 1, n//level)
        for l in range(1, level+1):
            for y in space:
                yield l, y
        for _ in range(tail):
            yield level, 1
        yield None

    def rule(self, inpt):
        if inpt == 'A':
            return ['B', '-', 'A', '-', 'B']
        else:
            return ['A', '+', 'B', '+', 'A']

    def generate(self, level):
        if level == 0:
            return []
        res = []
        for i in range(1, level+1):
            if i == 1:  # axiom
                res = ['A']
                continue
            for j, v in enumerate(res):
                if v == '-' or v == '+':
                    continue
                n_res = self.rule(v)
                del res[j]
                res.insert(j, n_res)
            res = reduce(iconcat, res, [])
        return res

    def turtle(self, cr: cairo.Context, command, theta, delta=1.0):
        cr.move_to(self.x, self.y)
        if command == 'A':
            angles = [i*self.angle for i in reversed(range(-1, 2))]
        else:
            angles = [i * self.angle for i in range(-1, 2)]
        for a in angles:
            ca = self.length*cos(a)
            t = (theta > 0) - (theta < 0)
            p1 = self.length*exp(1j*(a+theta))
            p0 = ca*exp(1j*(theta))
            px = self.x + ((p1-p0)*delta + p0).real
            py = self.y + ((p1-p0)*delta + p0).imag

            cr.line_to(px, py)
            self.x, self.y = px, py

    def turtle_draw(self, cr: cairo.Context, delta=1.0):
        if self.level == 0:
            cr.move_to(self.x, self.y)
            cr.line_to(self.length, self.y)
            cr.stroke()
            return
        init_angle = 0 if self.turtle_path[0] == 'A' else self.angle
        for command in self.turtle_path:
            if command == 'A':
                self.turtle(cr, command, init_angle, delta=delta)
                # self.turtle(cr, command, self.angle+0.1, delta=delta)
            elif command == 'B':
                self.turtle(cr, command, init_angle, delta=delta)
            elif command == '+':
                init_angle += self.angle
            elif command == '-':
                init_angle -= self.angle
        cr.stroke()

    def movie(self, cr: cairo.Context):
        if self.animate_val is None and self.on_first_frame:
            self.on_first_frame = False
            return
        elif self.animate_val is None:
            cr.set_source_rgb(*hex2rgb(colors[1]))
            self.turtle_draw(cr, delta=1)
        else:
            l, d = self.animate_val
            if self.current_level != l:
                self.length = 1 / (2 << (l - 1)) if l > 0 else 1
                self.turtle_path = self.generate(l)
                self.current_level = l
                # self.line_color = interpolate(colors[l], colors[l-1], self.frames // self.level)
            try:
                cr.set_source_rgb(*next(self.line_color))
            except StopIteration:
                cr.set_source_rgb(*hex2rgb(colors[1]))
            self.turtle_draw(cr, delta=d)

    def on_draw(self, wd, cr: cairo.Context):
        cr.identity_matrix()

        mat = cairo.Matrix(self.width, 0, 0, -self.height, 0, self.height)
        cr.set_matrix(mat)
        # Background
        cr.rectangle(0, 0, 1, 1)
        cr.set_source_rgb(*hex2rgb(colors[-1]))
        cr.fill()
        # Set line colors
        cr.set_line_width(5e-3)
        self.x, self.y = 0, 0.05
        if self.delta is None:
            cr.set_source_rgb(*self.line_color)
            for i, c in zip(linspace(1, 0, 4), colors[:4]):
                self.x, self.y = 0, 0.05
                cr.set_source_rgba(*hex2rgb(c))
                self.turtle_draw(cr, delta=i)
        else:
            self.movie(cr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Name Here')
    parser.add_argument('--w', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--h', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--l', type=int, default=1, help='Initial level')
    parser.add_argument('--fr', type=int, default=100, help='Number of frames')
    parser.add_argument('--im', action='store_false', help='Use GTK window')
    parser.add_argument('--an', action='store_true', help='Animate')

    args = parser.parse_args()
    app = Sier_Arrow(args.w, args.h, args.im, args.an, args.fr, args.l)
    if args.im:
        if args.an:
            GLib.timeout_add(50, app.gtk_move)
        Gtk.main()
