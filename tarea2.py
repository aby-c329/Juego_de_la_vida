import os
import time
import argparse
import cProfile
import pstats
import numpy as np
import pygame
from multiprocessing import Pool
import csv
import matplotlib.pyplot as plt


from line_profiler import profile

class GameOfLife:
    def __init__(self, nxC=60, nyC=60):
        os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        pygame.init()
        self.nxC, self.nyC = nxC, nyC
        self.gameState = np.zeros((nxC, nyC), dtype=int)
        self._init_pattern()
        self.pauseExec = False  # para simular sin pausa

    def _init_pattern(self):
        posX = (self.nxC//2)-3; posY = (self.nyC//2)-5
        coords = [(0,0),(1,0),(2,0),(3,0),(3,1),(3,2),(0,3),(3,3),(0,4),(1,4),(2,4),(3,4)]
        for dx, dy in coords:
            self.gameState[posX+dx, posY+dy] = 1

    @profile
    def _count_neighbors(self, x, y):
        tot = 0
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx or dy:
                    tot += self.gameState[(x+dx)%self.nxC, (y+dy)%self.nyC]
        return tot

    @profile
    def _update_state(self, new):
        for x in range(self.nxC):
            for y in range(self.nyC):
                n = self._count_neighbors(x,y)
                if self.gameState[x,y]==0 and n==3:
                    new[x,y]=1
                elif self.gameState[x,y]==1 and (n<2 or n>3):
                    new[x,y]=0

    def step(self):
        new = self.gameState.copy()
        self._update_state(new)
        self.gameState[:] = new


CONFIG = {'nx':512, 'ny':512, 'steps':100}
THREAD_COUNTS = [1,2,4,8]
CELLS_PER_THREAD = 10000

def bench_strong():
    def worker(_):
        g = GameOfLife(nxC=CONFIG['nx'], nyC=CONFIG['ny'])
        for _ in range(CONFIG['steps']): g.step()

    t1 = time.time(); worker(None); t1 = time.time()-t1
    results = []
    for p in THREAD_COUNTS:
        start = time.time()
        with Pool(p) as pool:
            pool.map(worker, range(p))
        tp = time.time()-start
        s = t1/tp; e = s/p
        results.append((p,tp,s,e))
    with open('strong_scaling.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['threads','time_s','speedup','efficiency']); w.writerows(results)
    print('strong_scaling.csv generado')


def bench_weak():
    def worker_size(arg):
        size, steps = arg
        g = GameOfLife(nxC=size, nyC=size)
        for _ in range(steps): g.step()

    t1 = time.time()
    size1 = int((CELLS_PER_THREAD*1)**0.5)
    worker_size((size1,50)); t1 = time.time()-t1
    results = []
    for p in THREAD_COUNTS:
        size = int((CELLS_PER_THREAD*p)**0.5)
        start = time.time()
        with Pool(p) as pool:
            pool.map(worker_size, [(size,50)]*p)
        tp = time.time()-start
        e = t1/(tp*p)
        results.append((p,tp,e))
    with open('weak_scaling.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['threads','time_s','efficiency']); w.writerows(results)
    print('weak_scaling.csv generado')


def run_cprofile(nx,ny,steps,out):
    def sim():
        g = GameOfLife(nxC=nx, nyC=ny)
        for _ in range(steps): g.step()
    pr = cProfile.Profile(); pr.enable(); sim(); pr.disable()
    pr.dump_stats(out)
    with open('cprofile.txt','w') as f:
        ps= pstats.Stats(pr,stream=f)
        ps.strip_dirs().sort_stats('cumulative').print_stats()
    print(f'Perfil cProfile -> {out}, cprofile.txt')

def plot_scaling():
    # Fuerte
    t,s,e = [],[],[]
    with open('strong_scaling.csv') as f:
        for r in csv.DictReader(f): t.append(int(r['threads'])); s.append(float(r['speedup'])); e.append(float(r['efficiency']))
    plt.figure(); plt.plot(t,s,marker='o'); plt.xlabel('Hilos'); plt.ylabel('Speedup'); plt.savefig('strong_speedup.png')
    plt.figure(); plt.plot(t,e,marker='o'); plt.xlabel('Hilos'); plt.ylabel('Eficiencia'); plt.savefig('strong_efficiency.png')
    # Débil
    t2,ti,e2 = [],[],[]
    with open('weak_scaling.csv') as f:
        for r in csv.DictReader(f): t2.append(int(r['threads'])); ti.append(float(r['time_s'])); e2.append(float(r['efficiency']))
    plt.figure(); plt.plot(t2,ti,marker='o'); plt.xlabel('Hilos'); plt.ylabel('Tiempo (s)'); plt.savefig('weak_time.png')
    plt.figure(); plt.plot(t2,e2,marker='o'); plt.xlabel('Hilos'); plt.ylabel('Eficiencia'); plt.savefig('weak_efficiency.png')
    print('Gráficas generadas')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Pipeline Performance Juego de la Vida')
    sp = p.add_subparsers(dest='cmd')
    # perfil
    p0 = sp.add_parser('profile')
    p0.add_argument('--nx', type=int, default=512)
    p0.add_argument('--ny', type=int, default=512)
    p0.add_argument('--steps', type=int, default=100)
    p0.add_argument('--out', type=str, default='perf.pstats')
    # line-profiler
    sp.add_parser('line')
    # bench
    sp.add_parser('strong')
    sp.add_parser('weak')
    # plot
    sp.add_parser('plot')

    args = p.parse_args()
    if args.cmd == 'profile':
        run_cprofile(args.nx, args.ny, args.steps, args.out)
    elif args.cmd == 'line':
        # llama a kernprof externamente
        os.system(f'kernprof -l -v {__file__}')
    elif args.cmd == 'strong':
        bench_strong()
    elif args.cmd == 'weak':
        bench_weak()
    elif args.cmd == 'plot':
        plot_scaling()
    else:
        p.print_help()
