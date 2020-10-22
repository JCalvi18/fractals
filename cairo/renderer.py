import cairo
import cv2
import numpy as np
import gi
from tqdm import tqdm
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class Renderer(Gtk.Window):
    def __init__(self, width, height, gtk, animate=None, frames=0):
        self.width = width
        self.height = height
        self.frames = frames
        if gtk:
            super().__init__()
            self.init_ui()
            self.animate_val = None
            if animate is not None:
                self.animate_iter = animate  # This must be function or generator defined in the child
        else:
            #self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            # cr = cairo.Context(self.surface)
            # if animate is not None:
            #     self.animate_iter = animate
            #     self.animate(cr)
            # else:
            #     self.on_draw(None, cr)
            #     self.surface.write_to_png('image.png')
            #     cr.show_page()
            # self.surface.finish()
            with cairo.SVGSurface("vector_graph.svg", 200, 200) as surface:
                cr = cairo.Context(surface)
                self.on_draw(None, cr)

    def init_ui(self):
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)
        self.darea = darea

        self.set_title("GTK Cairo")
        self.resize(self.width, self.height)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_draw(self, wd, cr: cairo.Context):
        pass

    def gtk_move(self):
        self.darea.queue_draw()
        self.animate_val = next(self.animate_iter)
        if self.animate_val is not None:
            return True
        else:
            return False

    def animate(self, cr: cairo.Context, fps=30):
        out = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (self.width, self.height))

        for _ in tqdm(range(self.frames)):
            self.animate_val = next(self.animate_iter)
            self.on_draw(None, cr)
            cr.show_page()
            buf = self.surface.get_data()
            render = np.ndarray(shape=(self.width, self.height, 4), dtype=np.uint8, buffer=buf)
            render = cv2.cvtColor(render, cv2.COLOR_RGBA2RGB)
            out.write(render)
        out.release()
