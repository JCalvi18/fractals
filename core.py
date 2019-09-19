import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool,Lock
import os
import torch as t


class Fractal(object):
    def __init__(self, resolution=[100, 100], point=[-1.7492199, -0.000335], scale=1.875e-05, nrep=200):
        self.resolution = resolution
        self.point = point
        self.scale = scale
        self.width = [1.25*self.scale, 1*self.scale]
        self.nrep = nrep
        self.M = t.Tensor(np.zeros(resolution, dtype=np.int16)).cuda()

    def get_args(self):

        x_lim = [self.point[0]-self.width[0], self.point[0]+self.width[0]]
        y_lim = [self.point[1]+self.width[1], self.point[1]-self.width[1]]

        x0 = np.linspace(x_lim[0], x_lim[1], self.resolution[0], dtype='double')
        x0 = np.tile(x0, self.resolution[1])
        y0 = np.linspace(y_lim[1], y_lim[0], self.resolution[1], dtype='double')
        y0 = np.repeat(y0, self.resolution[0])
        return zip(x0, y0, range(self.resolution[0]*self.resolution[1]))

    def update_matrix(self,args):
        #args[0]=index
        #args[1]=val
        self.M[args[0]]=args[1]


class Fractal_GUI(Fractal):
    def __init__(self,*args,**kwargs):
        super(Fractal_GUI, self).__init__(*args,**kwargs)
        self.fig, self.ax = plt.subplots()
        self.mv=4
        self.point_text=plt.text(0.02, .9, str('Point: '+str(self.point)), fontsize=14, transform=plt.gcf().transFigure)
        self.scale_text=plt.text(0.02, .8, str('Scale: '+str(self.scale)), fontsize=14, transform=plt.gcf().transFigure)

    def print_text(self):
        self.point_text.remove()
        self.point_text=plt.text(0.02, .9, str('Point: '+str(self.point)), fontsize=14, transform=plt.gcf().transFigure)
        self.scale_text.remove()
        self.scale_text=plt.text(0.02, .8, str('Scale: '+str(self.scale)), fontsize=14, transform=plt.gcf().transFigure)
    def event_update(self,event):
        if event.key=='left':
            self.point[0]-=self.scale/self.mv
        elif event.key=='right':
            self.point[0]+=self.scale/self.mv
        elif event.key=='up':
            self.point[1]-=self.scale/self.mv
        elif event.key=='down':
            self.point[1]+=self.scale/self.mv
        elif event.key=='z':
            self.scale/=2
            self.width=[1.25*self.scale,1*self.scale]
        elif event.key=='x':
            self.scale*=2
            self.width=[1.25*self.scale,1*self.scale]
        elif event.key=='c':
            self.copy()
        elif event.key=='escape':
            return 0
        self.print_text()

        return 1

    def show(self):
        self.ax.imshow(self.M.reshape(self.resolution),interpolation='nearest')
        plt.draw()

    def copy(self):
        s=str('python server.py -px '+str(self.point[0])+' -py '+str(self.point[1])+' -s '+str(self.scale))
        os.system('echo %s |xclip -selection c'%s)


class Artist_GUI(object):
    """docstring for Artist_GUI"""
    def __init__(self, arg):
        super(Artist_GUI, self).__init__()
        self.arg = arg


def mandelbrot(args):
    x,y,i,nrep=args
    r=im=it=0
    while r**2 + im**2 < 4  and  it < nrep:
        aux = r**2 - im**2 + x
        im = 2*r*im + y
        r = aux
        it+=1
    return i,it


def gen(frac_type, frac_class):
    p = Pool()
    for x,y,i in frac_class.get_args():
        res=p.apply_async(frac_type, args=((x,y,i,frac_class.nrep),),callback=frac_class.update_matrix)
    p.close()
    p.join()


def event_handler(event, frac):
    if frac.event_update(event):
        gen(mandelbrot, frac)
        frac.show()
    else:
        plt.close()



