import cairo
import argparse
import cv2
import numpy as np
import gi
from tqdm import tqdm
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


def hex2rgb(h):
    v = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return [x/255 for x in v]


colors = ['0e3b43', '2a8a33', '3F00FF', '0165a9', 'f0a202', '00a9a5', '1c448e', 'FFFFFF']
colors = [hex2rgb(h) for h in colors]


class Sierpinski(Gtk.Window):

    def __init__(self, width, height, level, sc, gtk, animate, frames):
        self.width = width
        self.height = height
        self.sc = sc
        self.level = level
        self.frames = frames
        self.triangle = self.s_triangle(level)
        self.dx = 1.0 / (2 ** level)
        self.dy = 1.0 / (2 ** (level - 1))
        self.lw = 0.0005
        self.al = 1.0
        if gtk:
            super(Sierpinski, self).__init__()
            self.init_ui()
            if animate:
                self.sc_gen = self.geo_gen(sc, 1, frames)
                self.lw_gen = self.geo_gen(self.lw, 1e-5, frames)
                self.al_gen = self.geo_gen(self.al, 0.8, frames)
        else:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(self.surface)
            if animate:
                self.animate(cr)
            else:
                self.on_draw(None, cr)
                self.surface.write_to_png('image.png')
                cr.show_page()
            self.surface.finish()

    def geo_gen(self, start, stop, n):
        for i in np.geomspace(start, stop, n):
            yield i
        yield 0

    def reverse_line(self):
        for r in range(int((2 ** self.level) / 2)):
            yield self.triangle[-(1 + r * 2)], self.triangle[-(2 + r * 2)]

    def s_triangle(self, level):
        triangle = [[1], [1] * 2]
        if level < 2:
            return triangle

        prev = triangle[1]
        for _ in range(2 ** level - 2):
            line = [1]
            for i, j in zip(prev[1:], prev[:-1]):
                line.append(i ^ j)
            line.append(1)
            triangle.append(line)
            prev = line
        return triangle

    def draw_triag(self, cr: cairo.Context, p):
        # p-> lower left coordinate of the triangle
        cr.move_to(*p)  # lower left

        cr.rel_line_to(2 * self.dx, 0)  # line to lower right
        cr.rel_line_to(-self.dx, -self.dy)
        cr.close_path()

    def init_ui(self):
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)
        self.darea = darea

        self.set_title("GTK window")
        self.resize(self.width, self.height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def background(self, cr: cairo.Context):

        linear = cairo.LinearGradient(0, 0, .25, 1)
        linear.add_color_stop_rgb(0.0, *colors[0])
        linear.add_color_stop_rgb(0.4, *colors[5])
        linear.add_color_stop_rgb(1.0, *colors[6])

        cr.rectangle(0, 0, .5, 1)
        cr.set_source(linear)
        cr.fill()

        cr.rectangle(0.5, 0, 1, 1)

        linear = cairo.LinearGradient(1, 0, .75, 1)
        linear.add_color_stop_rgb(0.0, *colors[0])
        linear.add_color_stop_rgb(0.4, *colors[5])
        linear.add_color_stop_rgb(1.0, *colors[6])
        cr.set_source(linear)
        cr.fill()

        cr.move_to(.5, 0)  # lower left
        cr.rel_line_to(-.5, 1)
        cr.rel_line_to(1, 0)
        cr.close_path()

        radial = cairo.RadialGradient(0.5, 0.5, 0.1, 0.5, 0.5, 0.75)
        radial.add_color_stop_rgba(0, *colors[3], 0.7)
        radial.add_color_stop_rgba(.4, *colors[1], 0.5)
        radial.add_color_stop_rgba(1, *colors[2], 0.1)

        cr.set_source(radial)
        cr.fill()

    def on_draw(self, wd, cr: cairo.Context, sc=None, lw=None, al=None):
        # setup scale
        if sc is None:
            sc = self.sc
            lw = self.lw
            al = self.al
        cr.identity_matrix()
        cr.scale(self.width*sc, self.height*sc)
        tx = (sc-1)/(sc*2)
        cr.translate(-tx, 0)

        self.background(cr)
        # triangle
        p = [0.0, 1.0]
        for r0, r1 in self.reverse_line():  # iterate thought rows
            pc = p.copy()
            for n, _ in enumerate(r0):
                if n % 2:
                    continue
                if (r0[n] and r1[n]) and (r0[n + 1] and r1[n]):
                    self.draw_triag(cr, pc)
                pc[0] += 2 * self.dx
            p = [p[0] + self.dx, p[1] - self.dy]

        cr.set_line_width(lw)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke_preserve()
        cr.set_source_rgba(*colors[4], al)
        cr.fill()

    def gtk_move(self):
        self.darea.queue_draw()
        self.sc = next(self.sc_gen)
        self.lw = next(self.lw_gen)
        self.al = next(self.al_gen)
        if self.sc > 1:
            return True
        else:
            return False

    def animate(self, cr: cairo.Context, fps=30):
        out = cv2.VideoWriter('sp.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (self.width, self.height))
        scales = np.geomspace(self.sc, 1, self.frames)
        line_w = np.geomspace(self.lw, 1e-5, self.frames)
        alpha = np.geomspace(self.al, 0.8, self.frames)

        for s, lw, a in tqdm(zip(scales, line_w, alpha), total=self.frames):
            self.on_draw(None, cr, sc=s, lw=lw, al=a)
            cr.show_page()
            buf = self.surface.get_data()
            render = np.ndarray(shape=(self.width, self.height, 4), dtype=np.uint8, buffer=buf)
            render = cv2.cvtColor(render, cv2.COLOR_RGBA2RGB)
            out.write(render)
        for _ in range(150):
            out.write(render)
        out.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Sierpinski generator')
    parser.add_argument('l', type=int, default=1, help='Level of the triangle')
    parser.add_argument('--w', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--h', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--s', type=int, default=1, help='Initial Scale')
    parser.add_argument('--fr', type=int, default=100, help='Number of frames')
    parser.add_argument('--gtk', action='store_true', help='Use GTK window')
    parser.add_argument('--an', action='store_true', help='Animate')

    args = parser.parse_args()
    app = Sierpinski(args.w, args.h, args.l, args.s, args.gtk, args.an, args.fr)
    if args.gtk:
        if args.an:
            GLib.timeout_add(100, app.gtk_move)
        Gtk.main()
