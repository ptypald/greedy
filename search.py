#!/usr/bin/python

from __future__ import print_function
import sys
from scanf import scanf
import signal

T = None
C = None
numlanes = None
numsteps = None
vd = None
x0 = None
y0 = None
v0 = None
n = None
obst_x = []
obst_y = []
obst_v = []

def stdin_data():
    global logfile

    data = []
    while True:
        try:
            s = sys.stdin.readline()
            #logfile.write(s)
            if (s == "\n"): break
            data.append(s[0:-1])
        except (EOFError, KeyboardInterrupt):
            break
    return data

def cost(xnew, ynew, vnew, dy, dv, u, k):
    global obst_x
    global obst_y
    global C
    global n
    global vd

    for i in range(n):
        if (obst_y[i][k+1] == ynew): 
            if (abs(obst_x[i][k+1] - xnew) <= 1.5 * C):
                return 10e6

        if (obst_y[i][k+1] == (ynew - dv)): 
            if (abs(obst_x[i][k+1] - xnew) <= 1.5 * C):
                return 10e6

    return abs(u) + abs(dy) + 100*abs(vnew - vd)

def cost2(xold, xnew, ynew, vnew, dy, dv, u, k):
    return  cost(0.5*(xold+xnew), ynew, vnew, dy, dv, u, k) + cost(xnew, ynew, vnew, dy, dv, u, k)

def xprint(msg):
    print(msg)
    logfile.write(msg + "\n")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def greedy(x0, y0, v0):
    global numsteps, T

    x = {0: x0}
    y = {0: y0}
    v = {0: v0}
    ux = {}
    c = {}
    cbest_sum = 0

    # consider each step
    for k in range(numsteps-1):
        cbest = float("inf")    # best cost seen so far

        for dy in [+1, 0, -1]:
            ynew = y[k] + dy
            if (ynew < 0 or ynew >= numlanes):
                continue

            #dxopts = [q*v[k]*T for q in [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0]]
            #uxopts = [2*(dx - v[k]*T)/pow(T,2) for dx in dxopts] + [0.1, 0.2, 0.3]

            dxopts = [q*v[k]*T for q in [1.0, 0.1]]
            uxopts = [2*(dx - v[k]*T)/pow(T,2) for dx in dxopts] + [1.0, 1.5]

            for u in uxopts:
                dv = u*T
                vnew = v[k] + dv
                if (vnew < 0):
                    continue

                xnew = x[k] + v[k]*T + 0.5*u*pow(T,2)

                cnew = cost2(x[k], xnew, ynew, vnew, dy, dv, u, k)
                #print("//\t\tk: %d, y: %.1f -> %.1f, v: %.1f -> %.1f, x: %.1f -> %.1f, cost: %.1f" %
                #(k, y[k], ynew, v[k], vnew, x[k], xnew, cnew))

                if (cnew < cbest):
                    cbest  = cnew
                    x[k+1] = xnew
                    y[k+1] = ynew
                    v[k+1] = vnew
                    ux[k] = u
                    c[k] = cnew

            # endfor

        # endfor
        cbest_sum += cbest

    # endfor
    return cbest_sum

class Solution:
    def __init__(self):
        self.k = None
        self.x = None
        self.y = None
        self.v = None
        self.c = float('inf')
        self.ux = None
        self.uy = None
        return

leaf = 0
best = {} 
path = {}
search_stop = 0

def expand(parent):
    global leaf, best, path, numsteps, T, search_stop

    if (search_stop and leaf > 0 or search_stop > 1):
        return

    path[parent.k] = parent
    if (parent.k == numsteps-1):
        leaf += 1
        if (parent.c < best["c"]):
            # eprint("cost %.1f at leaf %d" % (best["c"], leaf))
            best["c"] = parent.c
            best["x"] = [path[z].x for z in path]
            best["y"] = [path[z].y for z in path]
            best["v"] = [path[z].v for z in path]
            best["ux"] = [path[z].ux for z in path]
            best["uy"] = [path[z].uy for z in path]
        return

    if (parent.c >= best["c"]):
        return

    # proceed to create children
    child = Solution()
    child.k = parent.k + 1


    dxopts = [q*parent.v*T for q in [1.0, 0.1]]
    uxopts = [2*(dx - parent.v*T)/pow(T,2) for dx in dxopts] + [1.0, 1.5]
    #uxopts = [0.0, -1.0, +1.0]

    for ux in uxopts:
        parent.ux = ux

        child.v = parent.v + parent.ux * T
        if (child.v < 0):
            continue

        for uy in [0, -1, +1]:
            parent.uy = uy
            child.y = parent.y + parent.uy

            if (child.y < 0 or child.y >= numlanes):
                continue

            child.x = parent.x + parent.v * T + 0.5*parent.ux*T*T
            child.c = parent.c + cost2(parent.x, child.x, child.y, child.v, parent.uy, parent.v - child.v, parent.ux, parent.k)
            expand(child)


def sigint_handler(sig, frame):
    global search_stop
    search_stop += 1

if (__name__ == '__main__'):

    logfile = open("data-search.js", "w+")

    #
    ## read problem
    #

    logfile.write("/*")
    for line in stdin_data():
        logfile.write(line + "\n")
        ret = scanf("\"x(%f)\":%f", line)
        if (ret != None):
            x0 = ret[1]
            continue

        ret = scanf("\"y(%f)\":%f", line)
        if (ret != None):
            y0 = ret[1]
            continue

        ret = scanf("\"v(%f)\":%f", line)
        if (ret != None):
            v0 = ret[1]
            continue

        ret = scanf("\"vd\":%f", line)
        if (ret != None):
            vd = ret[0]
            continue

        ret = scanf("\"numlanes\":%d", line)
        if (ret != None):
            numlanes = ret[0]
            continue

        ret = scanf("\"obst_x(%d)\":%f", line)
        if (ret != None):
            (idveh, x) = ret
            obst_x.append(x)
            continue

        ret = scanf("\"obst_y(%d)\":%f", line)
        if (ret != None):
            (idveh, y) = ret
            obst_y.append(y)
            continue

        ret = scanf("\"obst_v(%d)\":%f", line)
        if (ret != None):
            (idveh, v) = ret
            obst_v.append(v)
            continue

        ret = scanf("\"numsteps\":%d", line)
        if (ret != None):
            numsteps = ret[0]
            continue

        ret = scanf("\"T\":%f", line)
        if (ret != None):
            T = ret[0]
            continue

        ret = scanf("\"C\":%f", line)
        if (ret != None):
            C = ret[0]
            continue
    logfile.write("*/\n")

    #
    ## compute trajectory of obstacles
    #

    n = len(obst_x)
    for i in range(n):
        for k in range(numsteps):
            if (k == 0):
                obst_x[i] = {0: obst_x[i]}
                obst_y[i] = {0: obst_y[i]}
                obst_v[i] = {0: obst_v[i]}
                continue

            obst_v[i][k] = obst_v[i][k-1]
            obst_y[i][k] = obst_y[i][k-1]
            obst_x[i][k] = obst_x[i][k-1] + obst_v[i][k-1]*T

    #
    # greedy

    best["c"] = greedy(x0, y0, v0)
    eprint("greedy cost: %s" % best["c"])
    best["c"] = float("inf")

    #
    # branch-and-bound 
    #

    signal.signal(signal.SIGINT, sigint_handler)

    root = Solution()
    root.x = x0 
    root.y = y0
    root.v = v0
    root.k = 0
    root.c = 0

    expand(root)

    if (search_stop > 1):
        exit(0)

    #
    ## postprocess solution
    #
    x = best["x"]
    y = best["y"]
    v = best["v"]
    ux = best["ux"]
    uy = best["uy"]
    c = range(numsteps)

    #
    ## print solution
    #

    xprint("var Data = {")
    for k in range(numsteps):
        xprint("\"x(%d)\":%.1f," % (k, x[k]))
        xprint("\"y(%d)\":%.1f," % (k, y[k]))

        xprint("\"vx(%d)\":%.1f," % (k, v[k]))
        xprint("\"vy(%d)\":%.1f," % (k, 0))


    for k in range(numsteps-1):
        xprint("\"ux(%d)\":%.1f," % (k, ux[k]))
        xprint("\"uy(%d)\":%.1f," % (k, uy[k]))
        xprint("\"c(%d)\":%.1f," % (k, c[k]))
        xprint("\"aux(%d)\":%.1f," % (k, ux[k]))
        

    for k in range(numsteps):
        for i in range(n):
            xprint("\"obst_x(%d,%d)\":%.1f," % (i, k, obst_x[i][k]))
            xprint("\"obst_y(%d,%d)\":%.1f," % (i, k, obst_y[i][k]))

    xprint("\"n\":%d," % (n))
    xprint("\"k\":%d," % (numsteps))
    xprint("\"numlanes\":%d," % (numlanes))
    xprint("\"vd\":%f," % (vd))
    xprint("\"umax\":%f," % (0))
    xprint("\"Step\":%f," % (T))
    xprint("\"C\":%f," % (5.0))
    xprint("};")
