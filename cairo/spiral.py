import cairo
import argparse
import numpy as np
from renderer import hex2rgb, Renderer
from gi.repository import Gtk, GLib

colors = ['102542', '31588F', '3F00FF', '0165a9', 'EDA10E', 'ee3037', '006AFF', 'FFFFFF']
colors = [hex2rgb(h) for h in colors]


class Spiral(Renderer):
    def __init__(self, width, height, gtk, animate, frames):
        super().__init__(width, height, gtk, animate, frames)

    def on_draw(self, wd, cr: cairo.Context):
        cr.identity_matrix()

        mat = cairo.Matrix(self.width, 0, 0, -self.height, self.width / 2, self.height / 2)
        cr.set_matrix(mat)

        cr.rectangle(-1, -1, 3, 2)
        cr.set_source_rgb(*colors[0])
        cr.fill()
        cr.set_source_rgb(*colors[1])
        cr.set_line_width(5e-3)
        cr.move_to(0, 0)
        cr.line_to(1, 1)
        cr.stroke()


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Hypotrochoid animator')
    parser.add_argument('--w', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--h', type=int, default=500, help='Level of the triangle')
    parser.add_argument('--s', type=int, default=1, help='Initial Scale')
    parser.add_argument('--fr', type=int, default=300, help='Number of frames')
    parser.add_argument('--im', action='store_false', help='Use GTK window')
    parser.add_argument('--an', action='store_true', help='Animate')

    args = parser.parse_args()
    app = Spiral(args.w, args.h, args.im, args.an, args.fr)
    if args.im:
        if args.an:
            GLib.timeout_add(50, app.gtk_move)
        Gtk.main()
