import cairo
import argparse
import numpy as np
from render_events import Renderer
from color_interpolation import hex2rgb
from gi.repository import Gtk, GLib
from math import pi as PI

colors = ['FFFFFF', '00000', 'F24236', '0165a9', 'EDA10E', 'ee3037', '006AFF', 'FFFFFF']
colors = [hex2rgb(h) for h in colors]


class proto(Renderer):
    def __init__(self, width, height, gtk, animate, frames):
        self.gtk_mode = gtk
        self.matrix = cairo.Matrix(width / 2, 0, 0, -height / 2, width / 2, height / 2)

        self.mousePos = [.0, .0]
        self.inter_sections = []
        self.onDrag = None
        self.radius = 0.9
        self.delta_r = 0.03
        super().__init__(width, height, gtk, animate, frames)

    def normalize_mouse(self, x, y):
        return 2 * x / self.width - 1, 1 - 2 * y / self.height

    def motion_receiver(self, wd, event):
        if event.is_hint:
            mx, my = self.normalize_mouse(event.x, event.y)
            self.darea.queue_draw()
            self.mousePos = [mx, my]

    def button_press_receiver(self, wd, event):
        mx, my = self.normalize_mouse(*event.get_coords())
        for x, y in self.inter_sections:
            if(mx > x-self.delta_r and mx < x+self.delta_r) and (my > y-self.delta_r and my < y+self.delta_r):
                self.onDrag = (x, y)

    def button_release_receiver(self, wd, event):
        self.darea.queue_draw()
        self.onDrag = None

    def draw_base(self, cr: cairo.Context):
        cr.identity_matrix()
        cr.set_matrix(self.matrix)

        cr.rectangle(-1, -1, 2, 2)
        cr.set_source_rgb(*colors[0])
        cr.fill()

        if self.gtk_mode:
            cr.rectangle(-1, .65, .15, .35)
            cr.set_source_rgb(*colors[1])
            cr.fill()

        cr.set_source_rgb(*colors[1])
        cr.set_line_width(9e-3)

        cr.arc(0, 0, self.radius, 0, 2 * PI)
        # cr.stroke()
        for theta in np.linspace(0, 2 * PI, self.radio_button + 1):
            cr.move_to(0, 0)
            x, y = self.radius * np.cos(theta), self.radius * np.sin(theta)
            cr.line_to(x, y)
            if (x, y) not in self.inter_sections:
                self.inter_sections.append((x, y))
        cr.stroke()

    def draw_intersection(self, cr: cairo.Context, x, y):
        cr.set_source_rgba(*colors[2], 0.7)
        cr.arc(x, y, self.delta_r, 0, 2*PI)
        cr.fill()

    def check_intersection(self, cr, mx, my):
        for x, y in self.inter_sections:
            if(mx > x-self.delta_r and mx < x+self.delta_r) and (my > y-self.delta_r and my < y+self.delta_r):
                self.draw_intersection(cr, x, y)
                break

    def connect_line(self, cr: cairo.Context, x0, y0):
        cr.set_source_rgb(*colors[1])
        cr.set_line_width(9e-3)
        cr.move_to(x0, y0)
        cr.line_to(*self.mousePos)
        cr.stroke()
        cr.stroke()

    def on_draw(self, wd, cr: cairo.Context):
        self.draw_base(cr)
        if self.onDrag:
            self.draw_intersection(cr, *self.onDrag)
            self.connect_line(cr, *self.onDrag)
            self.check_intersection(cr, *self.mousePos)
        else:
            self.check_intersection(cr, *self.mousePos)



if __name__ == "__main__":
    parser = argparse.ArgumentParser('Name Here')
    parser.add_argument('--w', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--h', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--s', type=int, default=1, help='Initial Scale')
    parser.add_argument('--fr', type=int, default=300, help='Number of frames')
    parser.add_argument('--im', action='store_false', help='Use GTK window')
    parser.add_argument('--an', action='store_true', help='Animate')

    args = parser.parse_args()
    app = proto(args.w, args.h, args.im, args.an, args.fr)
    if args.im:
        if args.an:
            GLib.timeout_add(50, app.gtk_move)
        Gtk.main()
