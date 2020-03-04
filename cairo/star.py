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


# colors = ['102542', '398941', '3F00FF', '0165a9', 'f0a202', 'EC630E', '422310', 'FFFFFF']
colors = ['102542', '31588F', '3F00FF', '0165a9', 'EDA10E', 'ee3037', '006AFF', 'FFFFFF']
colors = [hex2rgb(h) for h in colors]


class Star(Gtk.Window):
    def __init__(self, width, height, gtk, animate, frames):
        self.width = width
        self.height = height
        self.frames = frames
        self.d = 0.01
        # self.d = 0.6
        if gtk:
            super(Star, self).__init__()
            self.init_ui()
            if animate:
                self.gen_r = self.linspace(self.d, 1.2, self.frames)
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

    def linspace(self, start, end, n):
        for t in np.linspace(start, end, n):
            yield t
        yield -1

    def line(self, d, d1, d2, x1, x2):
        s = (d-d1)*1/(d2-d1)
        return s*x2+(1-s)*x1

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

    def bezier(self, cr: cairo.Context, x0, y0, x1, y1, x2, y2, x3, y3):
        mesh_f = 35
        cr.set_line_width(0.5e-2)
        p = [[x0, y0], [x1, y1], [x2, y2], [x3, y3]]
        cr.move_to(*p[0])
        cr.curve_to(*p[1], *p[2], *p[3])
        cr.stroke()

        # cr.move_to(*p[0])
        #
        # for j in p[1:]:
        #     cr.line_to(*j)
        # cr.stroke()

        l = []
        for i in range(len(p)-1):
            lx = np.linspace(p[i][0], p[i+1][0], mesh_f)
            ly = np.linspace(p[i][1], p[i+1][1], mesh_f)
            l.append([lx, ly])
        cr.set_line_width(0.5e-3)
        for l1, l2 in zip(l[:-1], l[1:]):
            for ix, iy, jx, jy in zip(l1[0], l1[1], l2[0], l2[1]):
                cr.move_to(ix, iy)
                cr.line_to(jx, jy)
        cr.stroke()

    def hypotrochoid(self, cr: cairo.Context, r, R, d, theta=4*np.pi, n=1000, c=(0, 4), alpha=1.0):
        # t = self.theta
        th = np.linspace(0, theta, n)
        for t in th:
            ph = ((R-r)*np.cos(t)+d*np.cos((R-r)*t/r), (R-r)*np.sin(t)-d*np.sin((R-r)*t/r))
            if t == 0:
                cr.move_to(*ph)
                continue
            cr.line_to(*ph)
        cr.set_source_rgba(*colors[c[0]],alpha)
        cr.fill_preserve()
        cr.set_source_rgba(*colors[c[1]],alpha)
        cr.stroke()

    def hypo_scale(self, cr: cairo.Context, a, b, d=None):
        if d is None:
            f = self.d * a - b
        else:
            f = d * a - b
        mat = cairo.Matrix(self.width * f, 0, 0, -self.height * f, self.width / 2, self.height / 2)
        cr.set_matrix(mat)

    def on_draw(self, wd, cr: cairo.Context, d_an=None):
        cr.identity_matrix()
        # cr.scale(self.width*sc, self.height*sc)
        # tx = (sc-1)/(sc*2)
        # mat = cairo.Matrix(1, 0, 0, 1, .5*(1-self.width), .5*(self.height-1))
        mat = cairo.Matrix(self.width, 0, 0, -self.height, self.width/2, self.height/2)
        cr.set_matrix(mat)
        # cr.scale(self.width, self.height)
        # cr.translate(.5, .5)

        cr.rectangle(-1, -1, 3, 2)
        cr.set_source_rgb(*colors[1])
        cr.fill()

        cr.set_line_width(.5e-2)
        cr.set_source_rgb(0, 0, 0)
        # self.hypotrochoid(cr, .005, .2, self.d*2, theta=2 * np.pi, n=1000, c=(1, 2))

        if d_an is None:
            d = self.d
        else:
            d = d_an
        #
        if d < .7:
            self.hypotrochoid(cr, .005, .2, d, theta=2 * np.pi, n=1000)

        cr.set_line_width(.8e-2)
        if .25 < d < .8:
            if d_an is None:
                self.hypo_scale(cr, 1.9, .21)
            else:
                self.hypo_scale(cr, 1.9, .21,d)
            self.hypotrochoid(cr, .005, .2, d - .25, theta=2 * np.pi, n=1000, c=(1, 5))
        elif d >= .8:
            self.hypo_scale(cr, 1.9, .21, .8)
            a = self.line(d, 0.8, 1.2, 1, 0)
            self.hypotrochoid(cr, .005, .2, .8 - .25, theta=2 * np.pi, n=1000, c=(1, 5), alpha=a)

        if .459 < d < .8:
            cr.set_line_width(.2e-2)
            if d_an is None:
                self.hypo_scale(cr, 3.2921, 1.53)
            else:
                self.hypo_scale(cr, 3.2921, 1.53,d)
            self.hypotrochoid(cr, .005, .2, .2-d/6.3015, theta=2 * np.pi, n=1000, c=(0, 4))
            # self.hypotrochoid(cr, .005, .2, .2 + 8e-4 + d / 1000, theta=4 * np.pi, n=2000, c=(0, 4))
        elif d >= .8:
            cr.set_line_width(self.line(d, 0.8, 1.2, .2e-2, 0.5e-2))
            self.hypo_scale(cr, 3.2921, 1.53, .8)
            # self.hypotrochoid(cr, .005+8e-4+d/1000, .2, .2, theta=4 * np.pi, n=2000, c=(0, 4))
            self.hypotrochoid(cr, .005, .2, .2-d/6.3015, theta=2 * np.pi, n=1000, c=(0, 4))

    def gtk_move(self):
        self.darea.queue_draw()
        self.d = next(self.gen_r)
        if self.d >= 0:
            return True
        else:
            return False

    def animate(self, cr: cairo.Context, fps=30):
        out = cv2.VideoWriter('media/star.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (self.width, self.height))
        dan = np.linspace(self.d, 1.2, self.frames)
        for d in tqdm(dan):
            self.on_draw(None, cr, d_an=d)
            cr.show_page()
            buf = self.surface.get_data()
            render = np.ndarray(shape=(self.width, self.height, 4), dtype=np.uint8, buffer=buf)
            render = cv2.cvtColor(render, cv2.COLOR_RGBA2RGB)
            out.write(render)
        out.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Hypotrochoid animator')
    parser.add_argument('--w', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--h', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--s', type=int, default=1, help='Initial Scale')
    parser.add_argument('--fr', type=int, default=300, help='Number of frames')
    parser.add_argument('--gtk', action='store_true', help='Use GTK window')
    parser.add_argument('--an', action='store_true', help='Animate')

    args = parser.parse_args()
    app = Star(args.w, args.h, args.gtk, args.an, args.fr)
    if args.gtk:
        if args.an:
            GLib.timeout_add(50, app.gtk_move)
        Gtk.main()