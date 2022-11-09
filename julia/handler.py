import argparse
import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib import colormaps
import matplotlib.pyplot as plt


class Handler(object):
    params = {'font.size': 18,
              'toolbar': 'None',
              'axes.spines.left': False,
              'axes.spines.right': False,
              'axes.spines.top': False,
              'axes.spines.bottom': False,
              'ytick.left': False,
              'ytick.right': False,
              'xtick.bottom': False,
              'xtick.top': False,
              'xtick.labelbottom': 'off',
              'ytick.labelleft': 'off'}
    plt.rcParams.update (params)

    def __init__(self, name):
        with np.load(name) as f:
            if len(f.files) == 1:
                self.M = f[f.files[0]]
            else:
                self.M = [f[m] for m in f.files]
        cm_name = name.split('.')[0]+'_cm'+'.npz'
        self.make_cm(cm_name)

    def make_cm(self, name, linear=True):
        with np.load(name) as f:
            cdict = dict(f)
        if linear:
            self.cm = LinearSegmentedColormap('na', cdict)
            return

        anchors = [int(r[0]*256) for r in cdict['red']]
        slices = [slice (a0, a1) for a0, a1 in zip (anchors [:-1], anchors [1:])]
        static_colors = [np.array([r[1], g[1], b[1], 1.]) for r, g, b in zip(cdict['red'], cdict['green'], cdict['blue'])]
        viridis = colormaps ['viridis']
        cm = viridis (np.linspace (0, 1, 256))

        for c, s in zip(static_colors[:-1], slices):
            cm[s, :] = c
        self.cm = ListedColormap(cm)

    def show(self, dpi=80):
        px, py = self.M.shape
        size = (py/float(dpi), px/float(dpi))
        fig = plt.figure (figsize = size, dpi = dpi)
        ax = fig.add_axes ([0, 0, 1, 1])

        color_bar = np.linspace (1, 0, 256)
        color_bar = np.repeat (color_bar, 200).reshape (-1, 200)

        ax.imshow(self.M, cmap=self.cm, aspect='equal', interpolation='none')
        plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Fractal Divider')
    parser.add_argument('--n', type=str, help='name of the fractals file')
    args = parser.parse_args ()
    h = Handler(args.n)
    h.show()

