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
import pandas as pd
import numpy as np

import matplotlib.ticker as mticker
import gantt.utils as utils
import gantt.colour as colour


def plotTaskList(tasklist, colourby=None):
 
    if colourby is None:
        colourby = colour.ColourByStartDate(tasklist)

    offset = 0.1 * pd.to_timedelta('1D')

    ax = plt.gca()
    tl = tasklist
    num = len(tl)
    for i in range(len(tl)):
        task = tl[i]
        y1 = num - i
        plotTaskBox(ax, y1, task, colourby, offset)
        connectDependencies(tl, task.label, offset)
        #markTimeBox(y1, task)

    ax = plt.gca()
    # labels = list(map(lambda x: "%s: %s" %(x.label, x.description), tl))[::-1]
    labels = list(map(lambda x: "%s: %s.." %(x.label, x.description[:8]), tl))[::-1]
    labels = [""] + labels
    locator = mticker.IndexLocator(1, 0)
    
    #ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(locator)
    ax.yaxis.set_ticklabels(labels)
    mark_weekends()


def plotTaskBox(ax, y1, task, colourby, offset):
    x1 = task.start_date + offset 
    x2 = task.end_date - offset 
    width = x2-x1
    
    fc, ec = colourby(task)

    label = task.label  #Used to connect the artist back to the task
    patch = plt.Rectangle((x1, y1-.2), width=width, height=.4, fc=fc, ec=ec, label=label)
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
    unit = pd.to_timedelta('1D')
    num = len(tasklist)
    i2 = utils.find(label, tasklist)
    task2 = tasklist[i2]
    depends = task2.depend

    t2 = task2.start_date
    for n, d in enumerate(depends):
        i1 = utils.find(d, tasklist)
        priorTask = tasklist[i1]

        t1 = priorTask.end_date 
        plotConnector(num-i1, t1, num-i2, t2, offset)


def plotConnector(col1, t1, col2, t2, offset):
    fmt = 'k-'
    config = {'lw':1}

    delt = 0
    # if t2 - t1 > .5:
    #     delt = .25

    #delt += offset + .1 * np.random.rand()
    delt = .1 * np.random.rand() * offset
    plt.plot([t1-offset, t1+delt], [col1, col1], fmt, **config, zorder=+100)
    plt.plot([t1+delt, t1+delt], [col1, col2], fmt, zorder=-10, **config)
    plt.plot([t1+delt, t2+offset], [col2, col2], fmt, **config)


import matplotlib as mpl
def mark_weekends():
    """Plot grey bars to indicate night time in the central timezone"""
    t1, t2 = plt.xlim()
    t1 = mpl.dates.num2date(t1)
    t2 = mpl.dates.num2date(t2)
    print (t1, t2)

    day_start = pd.date_range(start=t1, end=t2, freq='D')

    #Edge case: First day of data set is Sunday
    day = day_start[0]
    if day.dayofweek == 6:
        delta = pd.to_timedelta("1D")
        handle = plt.axvspan(day-delta, day+delta, color='b', alpha=.1)
        plt.xlim(xmin=min(timestamps))

    for day in day_start:
        if day.dayofweek == 5:
            delta = pd.to_timedelta("2D")
            handle = plt.axvspan(day, day+delta, color='b', alpha=.1)

    try:
        handle.set_label("Weekend")
    except UnboundLocalError:
        #No weekends marked
        pass
    
