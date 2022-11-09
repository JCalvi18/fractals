import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
import pyperclip
import argparse

# export LD_PRELOAD=/usr/lib/libstdc++.so.6

class Artist_GUI(object):
    params = {'font.size': 18,
     'toolbar':'None',
     'axes.spines.left':False,
     'axes.spines.right':False,
     'axes.spines.top':False,
     'axes.spines.bottom':False,
     'ytick.left':False,
     'ytick.right':False,
     'xtick.bottom':False,
     'xtick.top':False,
     'xtick.labelbottom':'off',
     'ytick.labelleft':'off'}
    plt.rcParams.update(params)

    fig = plt.Figure()

    #Three main part of the GUI
    frac_ax=plt.axes([.3, 0, .7, 1])
    bar_ax=plt.axes([.2, 0, .1, 1])
    row_ax=plt.axes([0, 0, .2, 1])

    #Set colors
    frac_ax.set_facecolor('#d9f4c7')
    bar_ax.set_facecolor('#dbd3c9')
    row_ax.set_facecolor('#8cc7a1')

    #Define first controls
    row_ax.text(0.1, .95, 'Colors')
    plus_ax = plt.axes([.13, .935, .025, .05])
    plus_ax.set_facecolor('#8cc7a1')

    cm_ax = plt.axes([.13, 0, .04, .05])
    cm_ax.set_facecolor('#8cc7a1')

    plot_ax = plt.axes([.05, 0, .04, .05])
    plot_ax.set_facecolor('#8cc7a1')

    exp_ax = plt.axes([.0, 0, .04, .05])
    exp_ax.set_facecolor('#8cc7a1')

    bplus = Button(plus_ax, '+', hovercolor='#8cc7a1')
    bcmap = Button(cm_ax, 'CM', hovercolor='#8cc7a1')
    bplot = Button(plot_ax, 'P', hovercolor='#8cc7a1')
    expB = Button(exp_ax, 'E', hovercolor = '#8cc7a1')

    # Define Color Bar
    color_map = cm.get_cmap('inferno')
    color_bar = np.linspace(1, 0, 256)
    color_bar = np.repeat(color_bar, 2).reshape(-1, 2)
    bar_ax.imshow(color_bar, aspect='auto', cmap=color_map)

    # Define size for rows
    rec = [0, .8, .1, .1]

    # List of buttons and text widget
    up_buttons = []
    down_buttons = []
    paste_butons = []
    clear_buttons = []
    t_box = []

    axcolor = []
    axcolorid = []
    col_anch = []
    nrows = int(0)

    def __init__(self, name):
        self.name = name
        with np.load(name) as f:
            if len(f.files) == 1:
                self.M = f[f.files[0]]
            else:
                self.M = [f[m] for m in f.files]
        self.bplus.on_clicked(lambda event: self.add_button())
        self.bcmap.on_clicked(lambda event: self.gen_cm())
        self.bplot.on_clicked(lambda event: self.update_fr())
        self.expB.on_clicked (lambda event: self.export_cm())
        self.update_fr()

    def move_text(self, idx, inverse=False):
        if inverse:
            self.col_anch[idx], self.col_anch[idx + 1] = self.col_anch[idx + 1], self.col_anch[idx]
        else:
            self.col_anch[idx], self.col_anch[idx - 1] = self.col_anch[idx - 1], self.col_anch[idx]

    def bup(self, idx, move=True):
        if idx == 0:
            return

        cu = self.axcolor[idx].get_facecolor()
        cd = self.axcolor[idx-1].get_facecolor()

        self.axcolor[idx-1].set_facecolor(cu)
        self.axcolor[idx].set_facecolor(cd)

        self.move_text(idx)
        if move:
            self.t_box[idx][1].set_val(self.col_anch[idx])
            self.t_box[idx-1][1].set_val(self.col_anch[idx - 1])
        plt.draw()

    def bdown(self, idx):
        if idx == self.nrows-1:
            return
        cu = self.axcolor[idx].get_facecolor()
        cd = self.axcolor[idx+1].get_facecolor()

        self.axcolor[idx+1].set_facecolor(cu)
        self.axcolor[idx].set_facecolor(cd)

        self.move_text(idx, inverse=True)
        self.t_box[idx][1].set_val(self.col_anch[idx])
        self.t_box[idx+1][1].set_val(self.col_anch[idx + 1])

        plt.draw()

    def paste(self, idx):
        txt = pyperclip.paste()
        txt = str('#'+txt)
        self.axcolorid[idx].remove()
        if len(txt) != 7:
            self.axcolor[idx].set_facecolor('#FFFFFF')
            self.axcolorid[idx] = self.axcolor[idx].text(0.2, .4, 'Error', color=(0, 0, 0, .6))
        else:
            self.axcolor[idx].set_facecolor(txt)

        plt.draw()

    def clear(self, idx):
        for i in range(idx+1, self.nrows):
            self.bup(i, move=False)

        # remove all the buttons
        for l in [self.up_buttons, self.down_buttons, self.paste_butons, self.clear_buttons, self.t_box]:
            ax, b, cid = l[-1]
            b.disconnect(cid)
            ax.remove()
            l.pop()

        for l, v in zip(self.t_box, self.col_anch):
            l[1].set_val(v)

        self.axcolor[-1].remove()
        self.axcolor.pop()
        self.axcolorid.pop()
        self.col_anch.pop()
        plt.draw()

        self.rec[1] += .12
        self.nrows -= 1

    def text_summit(self, idx, text):
        val = float(text)
        if val <= 1:
            self.col_anch[idx] = float(text)
        else:
            self.col_anch[idx] = None
        plt.draw()

    def add_button(self):
        # Add a new color row
        # A color row contains a color ID and a numbers of repetitions, this will be used to create a color map
        # This object has 4 buttons:
        #   v-> to paste from clipboard
        #   x->
        if self.nrows > 6:
            return

        idx = self.nrows

        r = self.rec
        self.axcolor.append(plt.axes(r))
        self.axcolorid.append(self.axcolor[-1].text(0, .4, '#FFFFFF', color=(0, 0, 0, .6)))

        up = plt.axes([r[2], r[1]+r[3]-.02, .2-r[2], .02])
        b = Button(up, u'\u25B2', color='#009fb7', hovercolor='#2eb0c4')
        cid = b.on_clicked(lambda event:self.bup(idx))
        self.up_buttons.append((up, b, cid))

        down = plt.axes([r[2], r[1], .2-r[2], .02])
        b = Button(down, u'\u25BC', color='#009fb7', hovercolor='#2eb0c4')
        cid = b.on_clicked(lambda event:self.bdown(idx))
        self.down_buttons.append((down, b, cid))

        p = plt.axes([r[2], r[1]+.02, 0.02, .06])
        b = Button(p, 'V', color='#8ac926', hovercolor='#b4dc74')
        cid = b.on_clicked(lambda event:self.paste(idx))
        self.paste_butons.append((p, b, cid))

        d = plt.axes([.2-.02, r[1]+.02, .02, .06])
        b = Button(d, 'X', color='#cd5334', hovercolor='#da816b')
        cid = b.on_clicked(lambda event:self.clear(idx))
        self.clear_buttons.append((d, b, cid))

        t = plt.axes([r[2]+.02, r[1]+.02, .2-r[2]-.04, .06])
        init_txt = '1' if not idx else '0'
        b = TextBox(t, '', initial=init_txt)
        cid = b.on_submit(lambda text:self.text_summit(idx, text))
        self.t_box.append((t, b, cid))
        self.col_anch.append(float(init_txt))

        plt.draw()

        self.rec[1] -= .12
        self.nrows += 1

    def gen_cm(self):
        colors = [ac.get_facecolor() for ac in reversed(self.axcolor)]
        anchors = [ach for ach in reversed(self.col_anch)]
        if not all(anchors[1:]) > 0:
            return
        cdit = {cname: [[x, colors[xi][ci], colors[xi][ci]] for xi, x in enumerate(anchors)] for ci, cname in
                enumerate(['red', 'green', 'blue', 'alpha'])}
        self.color_map = LinearSegmentedColormap('na', cdit)
        self.bar_ax.imshow(self.color_bar, aspect='auto', cmap=self.color_map)

    def update_fr(self):
        self.frac_ax.imshow(self.M, cmap=self.color_map, aspect='equal', interpolation='bilinear')

    def export_cm(self):
        name = self.name.split('.')[0]+'_cm'+'.npz'

        colors = [ac.get_facecolor () for ac in reversed (self.axcolor)]
        anchors = [ach for ach in reversed (self.col_anch)]
        if not all (anchors [1:]) > 0:
            return
        cdic = {cname: [[x, colors [xi] [ci], colors [xi] [ci]] for xi, x in enumerate (anchors)] for ci, cname in
                enumerate (['red', 'green', 'blue', 'alpha'])}

        np.savez (name, **cdic)

parser = argparse.ArgumentParser('Fractal Color Artist')
parser.add_argument('--n', type=str, help='name of the fractals file')
# parser.add_argument('--bool', action='store_true', help='This is a boolean')
args = parser.parse_args()

gui = Artist_GUI(args.n)
plt.show()
