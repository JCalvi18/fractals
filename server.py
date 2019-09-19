import argparse
import numpy as np
from core import Fractal,mandelbrot,gen

def main(args):
	fr=Fractal(resolution=[args['resx'],args['resy']],point=[args['px'],args['py']],scale=args['s'],nrep=args['rep'])
	gen(mandelbrot,fr)
	np.savetxt('mn.txt', fr.M,fmt='%u')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Help Results')    
    parser.add_argument('-resx', help='Resolution',type=int,default=500)
    parser.add_argument('-resy', help='Resolution',type=int,default=500)
    parser.add_argument('-rep',help='Repetitions',type=int,default=100)
    parser.add_argument('-px', help='X Point',type=float,default=-1.74985)
    parser.add_argument('-py', help='Y Point',type=float,default=0)
    parser.add_argument('-s', help='Scale',type=float,default=3e-4)

    args = vars(parser.parse_args())                
    main(args)
