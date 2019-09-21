import numpy as np
import matplotlib.pyplot as plt
import os
import mxnet as mx
from mxnet import nd
from time import time


class Fractal(object):
    def __init__(self, resolution, point, scale=1.875e-05, nrep=200, device=-1, row_wise=True, debug=False):
        self.resolution = resolution
        self.point = point
        self.scale = scale
        self.wh = [1.25*self.scale, 1*self.scale]
        self.nrep = nrep
        self.row_wise = row_wise
        self.debug = debug
        self.ctx = mx.gpu(device) if device >= 0 else mx.cpu(0)
        self.M = np.zeros(resolution)
        if not self.row_wise:
            self.M = self.M.T

    def change(self, point, scale):
        self.point = point
        self.scale = scale

    def get_row_column(self):
        # Generate rows or columns of the C plane
        x_lim = [self.point[0]-self.wh[0], self.point[0]+self.wh[0]]
        y_lim = [self.point[1]+self.wh[1], self.point[1]-self.wh[1]]

        X = np.linspace(x_lim[0], x_lim[1], self.resolution[0], dtype='double')
        Y = np.linspace(y_lim[1], y_lim[0], self.resolution[1], dtype='double')
        if self.row_wise:
            for y in Y:
                yield [(x, y) for x in X]
        else:
            for x in Y:
                yield [(x, y) for y in Y]

    def gen(self, frac_type, chunk_size=2):
        cs = chunk_size
        chunk = []
        slices = []
        start_exec = time()
        chunk_time = np.array([])
        for i, r in enumerate(self.get_row_column()):
            chunk += r
            slices.append(slice((cs-1)*len(r), cs*len(r)))
            cs -= 1
            if cs:
                continue
            in_points = nd.array(chunk, ctx=self.ctx).T  # Points to evaluate
            init_vals = nd.zeros((3, in_points.shape[1]), ctx=self.ctx)  # initial values of r, im and it
            # Operations performed in GPU
            start_chunk = time()
            out_stream = frac_type(in_points, init_vals, self.nrep).asnumpy()
            if len(slices) > 1:
                slices.reverse()
                for j, s in zip(range((i+1)-chunk_size, i+1), slices):
                    self.M[j] = out_stream[s]
            else:
                self.M[i] = out_stream
            chunk_time = np.append(chunk_time, time()-start_chunk)

            cs = chunk_size
            slices = []
            chunk = []

        if self.debug:
            print('Plane generation:{:0.3f}s'.format(time()-start_exec))
            print('Average chunk execution:{:0.3f}s'.format(chunk_time.mean()))

class Fractal_GUI(Fractal):
    def __init__(self, *args, **kwargs):
        super(Fractal_GUI, self).__init__(*args, **kwargs)
        self.fig, self.ax = plt.subplots()
        self.mv = 4
        self.point_text = plt.text(0.02, .9, str('Point: '+str(self.point)), fontsize=14, transform=plt.gcf().transFigure)
        self.scale_text = plt.text(0.02, .8, str('Scale: '+str(self.scale)), fontsize=14, transform=plt.gcf().transFigure)

    def print_text(self):
        self.point_text.remove()
        self.point_text=plt.text(0.02, .9, str('Point: '+str(self.point)), fontsize=14, transform=plt.gcf().transFigure)
        self.scale_text.remove()
        self.scale_text=plt.text(0.02, .8, str('Scale: '+str(self.scale)), fontsize=14, transform=plt.gcf().transFigure)

    def event_update(self, event):
        if event.key == 'left':
            self.point[0] -= self.scale/self.mv
        elif event.key == 'right':
            self.point[0] += self.scale/self.mv
        elif event.key == 'up':
            self.point[1] -= self.scale/self.mv
        elif event.key == 'down':
            self.point[1] += self.scale/self.mv
        elif event.key == 'z':
            self.scale /= 2
            self.wh = [1.25*self.scale, 1*self.scale]
        elif event.key == 'x':
            self.scale *= 2
            self.wh = [1.25*self.scale, 1*self.scale]
        elif event.key == 'c':
            self.copy()
        elif event.key == 'escape':
            return 0
        self.print_text()

        return 1

    def show(self):
        self.ax.imshow(self.M, interpolation='nearest')
        plt.draw()

    def copy(self):
        s = '"frac.change([{:0.5f}, {:0.5f}], {})"'.format(self.point[0], self.point[1], self.scale)
        os.system('echo {} |xclip -selection c'.format(s))


def mandelbrot(points, init, nrep):
    x, y = points
    r, im, it = init
    for _ in range(nrep):
        mag = r**2 + im**2
        aux = r**2 - im**2 + x
        im = 2*r*im + y
        r = aux
        if all(mag >= 4):
            break
        it += mag < 4
    return it


def event_handler(event, frac):
    if frac.event_update(event):
        frac.gen(mandelbrot)
        frac.show()
    else:
        plt.close()



