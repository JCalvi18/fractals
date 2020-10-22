import cairo
import cv2
import numpy as np
from tqdm import tqdm
from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Renderer(Gtk.Window):
    def __init__(self, width, height, gtk, animate, frames=0):
        self.width = width
        self.height = height
        self.frames = frames
        self.video = None
        self.animation_cr = None
        if gtk:
            super().__init__()
            self.init_ui()
            self.animate_val = None
        else:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(self.surface)
            self.on_draw(None, cr)
            self.surface.write_to_png('image.png')
            cr.show_page()
            self.surface.finish()

    def init_ui(self):

        self.set_title("GTK Cairo")
        self.resize(self.width, self.height)
        self.set_position(Gtk.WindowPosition.CENTER)

        fixed = Gtk.Fixed()
        darea = Gtk.DrawingArea()
        darea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
        darea.connect("draw", self.on_draw)
        darea.connect('button_press_event', self.button_press_receiver)
        darea.connect('button_release_event', self.button_release_receiver)
        darea.set_size_request(self.width, self.height)
        # self.add(darea)
        self.darea = darea

        fixed.put(darea, 0, 0)

        next_button = Gtk.Button('Next')
        next_button.connect('button_press_event', self.calculate_next_gen)
        fixed.put(next_button, 10, 10)

        stamp_button = Gtk.Button('Stamp')
        stamp_button.connect('button_press_event', self.animate_frame)
        fixed.put(stamp_button, 100, 10)

        finish_button = Gtk.Button('Finish')
        finish_button.connect('button_press_event', self.finish_animation)
        fixed.put(finish_button, 200, 10)

        self.add(fixed)

        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_draw(self, wd, cr: cairo.Context):
        pass

    def finish_animation(self, widget, event):
        self.surface.finish()
        self.video.release()
        Gtk.main_quit()

    def calculate_next_gen(self, wd, event): pass

    def button_press_receiver(self, wd, event): pass

    def button_release_receiver(self, wd, event): pass

    def animate_frame(self, widget, event, fps=30, fr=5):
        if self.video is None:
            self.video = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (self.width, self.height))
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
            self.animation_cr = cairo.Context(self.surface)

        self.on_draw(None, self.animation_cr)
        self.calculate_next_gen(widget, event)
        self.animation_cr.show_page()
        buf = self.surface.get_data()
        render = np.ndarray(shape=(self.width, self.height, 4), dtype=np.uint8, buffer=buf)
        render = cv2.cvtColor(render, cv2.COLOR_RGBA2RGB)
        self.surface.show_page()
        for _ in range(fr):
            self.video.write(render)
