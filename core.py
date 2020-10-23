import torch
ctx = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os


from time import time


def hex2rgb(h):
    v = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(c/256 for c in reversed(v))


class Fractal(object):
    def __init__(self, resolution, point, scale=1.875e-05, nrep=200, row_wise=True, debug=False):
        self.resolution = resolution
        self.point = point
        self.scale = scale
        self.wh = [1.25*self.scale, 1*self.scale]
        self.nrep = nrep
        self.row_wise = row_wise
        self.debug = debug
        self.M = np.zeros(resolution, dtype=np.uint16)
        if not self.row_wise:
            self.M = self.M.T

        if ctx.type == 'cuda':
            print('Using %s' % torch.cuda.get_device_name(0))


    def change(self, point, scale):
        self.point = point
        self.scale = scale
        self.wh = [1.25 * self.scale, 1 * self.scale]

    def get_row_column(self):
        # Generate rows or columns of the C plane
        x_lim = [self.point[0]-self.wh[0], self.point[0]+self.wh[0]]
        y_lim = [self.point[1]+self.wh[1], self.point[1]-self.wh[1]]

        X = torch.linspace(x_lim[0], x_lim[1], self.resolution[0], dtype=torch.complex128)
        Y = torch.linspace(y_lim[1], y_lim[0], self.resolution[1], dtype=torch.complex128)*1j
        if self.row_wise:
            for y in Y:
                yield X+y
        else:
            for x in X:
                yield x+Y

    def gen(self, frac_type, chunk_size=2):
        cs = chunk_size
        chunk = None  # Tensor Pointer
        slices = []
        start_exec = time()
        chunk_time = np.array([])
        for i, r in enumerate(self.get_row_column()):
            if chunk is None:
                chunk = r
            else:
                chunk = torch.cat((chunk, r))
            slices.append(slice((cs-1)*len(r), cs*len(r)))
            cs -= 1
            if cs:
                continue
            # in_points = chunk.to(ctx)  # Points to evaluate

            in_points = chunk.cuda(ctx) if ctx.type == 'cuda' else chunk
            # Operations performed in GPU
            start_chunk = time()
            out_stream = frac_type(in_points, self.nrep)
            if len(slices) > 1:
                slices.reverse()
                for j, s in zip(range((i+1)-chunk_size, i+1), slices):
                    self.M[j] = out_stream[s]
            else:
                self.M[i] = out_stream
            chunk_time = np.append(chunk_time, time()-start_chunk)

            cs = chunk_size
            slices = []
            del chunk
            chunk = None

        if self.debug:
            print('Plane generation:{:0.3f}s'.format(time()-start_exec))
            print('Average chunk execution:{:0.3f}s'.format(chunk_time.mean()))


class Server(Fractal):
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.color_map = None
        plt.rcParams['figure.figsize'] = [10, 10]

    def run(self, frac_type, chunk_size=2, intpol='bilinear'):
        self.gen(frac_type, chunk_size)
        cm = 'hsv' if self.color_map is None else self.color_map
        plt.axis('off')
        plt.imshow(self.M, cmap=cm, interpolation=intpol)

    def export(self, name):
        np.savez_compressed(name, self.M)

    def save(self, name):
        cm = plt.cm.hsv if self.color_map is None else self.color_map
        norm = plt.Normalize(vmin=self.M.min(), vmax=self.M.max())

        # map the normalized data to colors
        # image is now RGBA (512x512x4)
        image = cm(norm(self.M))

        # save the image
        plt.imsave(name+'.jpg', image, dpi=1000)



class Explorer(Fractal):
    def __init__(self, *args, **kwargs):
        super(Explorer, self).__init__(*args, **kwargs)
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

    def gen_cm(self, hex_list, range_list):
        if len(hex_list) != len(range_list):
            return -1
        colors = [hex2rgb(h) for h in hex_list]

    def show(self):
        self.ax.imshow(self.M, interpolation='nearest')
        plt.draw()

    def copy(self):
        s = 'python gui.py --px {:0.5f} --py {:0.5f}'' --s {}'.format(self.point[0], self.point[1], self.scale)
        os.system('echo {} |xclip -selection c'.format(s))


def mandelbrot(c, nrep):

    z = c.clone().zero_()

    M = torch.zeros(z.shape, dtype=torch.int16, device=ctx)
    for _ in range(nrep):
        z = z**2+c
        if all(z.abs() >= 2):
            break
        M += z.abs() < 2

    if ctx.type == 'cuda':
        return M.cpu()
    else:
        return M


def event_handler(event, frac):
    if frac.event_update(event):
        frac.gen(mandelbrot, chunk_size=500)
        frac.show()
    else:
        plt.close()



