# -*- coding: utf-8 -*-
# Copyright 2017-2020 Orbital Insight Inc., all rights reserved.
# Contains confidential and trade secret information.
# Government Users:  Commercial Computer Software - Use governed by
# terms of Orbital Insight commercial license agreement.

"""
Created on Tue Jun 23 15:11:45 2020

@author: fergal
"""

from ipdb import set_trace as idebug
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.ticker as mticker
import utils
import colour

def sortTaskList(tasklist, sortby='startdate'):
    if sortby == 'startdate':
        keyfunc = lambda x: x.x
    elif sortby == 'enddate':
        keyfunc = lambda x: x.x + x.dur
    elif sortby == 'label':
        keyfunc = lambda x: x.label
    elif sortby == 'user':
        keyfunc = lambda x: x.user
    else:
        raise ValueError("Sort request not understood")

    return sorted(tasklist, key=keyfunc)

def plotTaskList(tasklist, colourby=None):

    if colourby is None:
        colourby = colour.ColourByStartDate(tasklist)

    offset = .1
    ax = plt.gca()
    tl = tasklist
    num = len(tl)
    for i in range(len(tl)):
        task = tl[i]
        y1 = num - i
        plotTaskBox(ax, y1, task, colourby, offset)
        connectDependencies(tl, task.label, offset)
        markTimeBox(y1, task)

    ax = plt.gca()
    # labels = list(map(lambda x: "%s: %s" %(x.label, x.description), tl))[::-1]
    labels = list(map(lambda x: "%s: %s.." %(x.label, x.description[:8]), tl))[::-1]
    labels = [""] + labels
    locator = mticker.IndexLocator(1, 0)

    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(locator)
    ax.yaxis.set_ticklabels(labels)


def plotTaskBox(ax, y1, task, colourby, offset):
    x1 = task.x + offset
    fc, ec = colourby(task)
    # ec = 'grey'

    label = task.label  #Used to connect the artist back to the task
    # plt.plot([x1, x2], [y1, y1], '-', color=clr, lw=8, label=label)
    width = task.dur - 2*offset
    patch = plt.Rectangle((x1, y1-.5), width=width, height=1, fc=fc, ec=ec, label=label)
    ax.add_artist(patch)


def markTimeBox(y1, task):
    plt.plot(task.startAfter, y1, 'k*')
    plt.plot(task.startBy + task.dur, y1, 'k*')


def markLateTask(x1, x2, y1):
    # config = {'lw':4, 'color':'r'}
    # patch = plt.Rectangle( (x1, y1), (x2-x1), .5, **config)
    # plt.gca().add_patch(patch)
    y1 += 0 #.25
    plt.plot([x1, x2], [y1, y1], 'w:', lw=8)
    # plt.plot([x1, x2], [y1, y1], 'y:', lw=8)


def connectDependencies(tasklist, label, offset):
    num = len(tasklist)
    i2 = utils.find(label, tasklist)
    task2 = tasklist[i2]
    depends = task2.depend

    t2 = task2.x
    for n, d in enumerate(depends):
        i1 = utils.find(d, tasklist)
        priorTask = tasklist[i1]

        t1 = priorTask.x + priorTask.dur
        plotConnector(num-i1, t1, num-i2, t2)


def plotConnector(col1, t1, col2, t2, offset=0):
    fmt = 'k-'
    config = {'lw':1}

    offset = .1

    delt = 0
    # if t2 - t1 > .5:
    #     delt = .25

    delt += -0.05 + .1 * np.random.rand()
    #plt.plot([t1, t2], [col1, col2], 'k-')
    plt.plot([t1-offset, t1+delt], [col1, col1], fmt, **config, zorder=+100)
    plt.plot([t1+delt, t1+delt], [col1, col2], fmt, zorder=-10, **config)
    plt.plot([t1+delt, t2+offset], [col2, col2], fmt, **config)
