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

        if gtk:
            super().__init__()
            self.init_ui()
            self.animate_val = None
            self.radio_button = 4
            if animate is not None:
                self.animate_iter = animate  # This must be function or generator defined in the child
        else:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(self.surface)
            if animate:
                self.animate_iter = animate
                self.animate(cr)
            else:
                self.on_draw(None, cr)
                self.surface.write_to_png('image.png')
                cr.show_page()
            self.surface.finish()

    def init_ui(self):

        self.set_title("GTK Cairo")
        self.resize(self.width, self.height)
        self.set_position(Gtk.WindowPosition.CENTER)

        fixed = Gtk.Fixed()
        draw_box = Gtk.Box()
        radio_box = Gtk.VBox()
        self.add(fixed)

        darea = Gtk.DrawingArea()
        darea.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK
                         | Gdk.EventMask.POINTER_MOTION_HINT_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
        darea.connect("draw", self.on_draw)
        darea.connect('motion_notify_event', self.motion_receiver)
        darea.connect('button_press_event', self.button_press_receiver)
        darea.connect('button_release_event', self.button_release_receiver)
        darea.set_size_request(self.width, self.height)
        # self.add(darea)
        self.darea = darea

        btn1 = Gtk.RadioButton(group=None, label="4")
        btn1.connect("toggled", self.radio_click)
        btn2 = Gtk.RadioButton(group=btn1, label="6")
        btn2.connect("toggled", self.radio_click)
        btn3 = Gtk.RadioButton(group=btn1, label="8")
        btn3.connect("toggled", self.radio_click)

        radio_box.add(Gtk.Label('Fold'))
        radio_box.add(btn1)
        radio_box.add(btn2)
        radio_box.add(btn3)

        draw_box.add(darea)

        fixed.put(draw_box, 0, 0)
        fixed.put(radio_box, 0, 0)


        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_draw(self, wd, cr: cairo.Context):
        pass

    def radio_click(self, widget, data=None):
        try: val = int(widget.get_label())
        except ValueError:
            print('Invalid Radio')
            val = 3
        if self.radio_button != val:
            self.darea.queue_draw()
            self.radio_button = val
            self.inter_sections = []

    def motion_receiver(self, darea, event):
        # receives drawing area, and EventStruct specified in Gdk.EventMask
        # https://developer.gnome.org/gtk-tutorial/stable/x2431.html
        pass

    def button_press_receiver(self, wd, event): pass

    def button_release_receiver(self, wd, event): pass

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
