from core import Explorer, event_handler, mandelbrot
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser('Mandelbrot fractal')
parser.add_argument('--r', type=int, default=20, help='Resolution for height and width (squared)')
parser.add_argument('--px', type=float, default=-1, help='Initial center point on X')
parser.add_argument('--py', type=float, default=0, help='Initial center point on Y')
parser.add_argument('--s', type=float, default=0.5, help='Initial scale')
parser.add_argument('--n', type=int, default=200, help='Number of repetitions')
parser.add_argument('--d', action='store_true', help='Flag to debug')
args = parser.parse_args()


frac = Explorer(resolution=[args.r]*2, point=[args.px, args.py], scale=args.s, nrep=args.n, debug=args.d, )
cid = frac.fig.canvas.mpl_connect('key_press_event', lambda event: event_handler(event, frac))


frac.gen(mandelbrot)
frac.show()
plt.show()