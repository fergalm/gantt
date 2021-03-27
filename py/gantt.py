# -*- coding: utf-8 -*-
"""
Created on Thu May 21 07:10:31 2020

TODO
o Plotting
    o Dependency lines
    o Colour code the boxes somehow
        o By user
        o By label name (1.* gets a colour?)
        o By status (blocked, inprogress, late, violates end date, ...)
    o Show earliest start and latest end lines
    o Add sort by user option
    o Highlight tasks that can't be completed on time

o Assign tasks to chains
o Sort tasks by chain, and position in chain, then re-optimize
o Convert input start/end dates from UTC to JD
o Adjust schedules for weekends
o Create per user schedule
o Propegate uncertainty through the chart
o check for integer labels, and raise an error
o Check for self dependency (at least at a single level)
@author: fergal
"""

from ipdb import set_trace as idebug
from pdb import set_trace as debug
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# import collections
import graphics
import critpath
import colour
import hover
import plot

class Task():
    """
    TODO
    --------
    Type checking
    """

    def __init__(self,
                 label,
                 description=None,
                 dur=None,
                 user=None,
                 depend=None,
                 startAfter=None,
                 startBy=None,
                 x=0):


        self.label=label
        self.description =description
        self.dur=dur
        self.user=user
        self.depend=depend
        self.startAfter=startAfter
        self.startBy=startBy
        self.x=x

    def __str__(self):
        strr = []
        for k in self.__dict__:
            val = "%s=%s" %(k, self.__dict__[k])
            strr.append(val)
        return '<' + " ".join(strr) + '>'

    def __repr__(self):
        return self.__str__()



def main(fn):
    raw= loadTable(fn)

    plt.clf()
    rough = roughSort(raw)
    # rough = critpath.sortByCriticalPath(raw)

    optimal = optimize(rough)
    sortedList = graphics.sortTaskList(optimal, 'user')
    clr = colour.ColourByUser(sortedList)
    # clr = colour.ColourByStartDate(sortedList)
    graphics.plotTaskList(sortedList, clr)

    clr.legend()
    handle = hover.Interact(sortedList)
    return handle



def loadTable(fn):
    """
    TODO
    ------
    o convert this to accept dates, not relative day numbers
    o Deal with whitespace in dependency list"""
    df = pd.read_csv(fn)

    tasklist = []

    x0 = 0
    for i, row in df.iterrows():
        if np.isnan(row.Duration):
            row.Duration = "1"

        if isinstance(row.Dependencies, float) and np.isnan(row.Dependencies):
            depend = []
        else:
            depend = row.Dependencies.split(',')

        if np.isnan(row.StartAfter):
            row.StartAfter = 0.

        if np.isnan(row.EndBy):
            row.EndBy= np.inf
        startBy = float(row.EndBy) - float(row.Duration)

        # idebug()
        t = Task(label = row.Label, \
                 description = row.Description, \
                 dur = float(row.Duration), \
                 user = row.Assignee, \
                 depend = depend, \
                 startAfter = float(row.StartAfter), \
                 startBy = startBy,\
                 x = x0,
                 )
        tasklist.append(t)

        x0 += t.dur

    return tasklist


def roughSort(tasklist, project_start_jd=0):
    maxLoop = 1000

    task = tasklist
        # print("\n".join(map(str, tasklist)))
    i = 0
    nloop = 0
    while i < len(tasklist) and nloop<maxLoop:
        # print("Looking at", i, task[i])
        deps = task[i].depend
        # print(deps)

        flag = False
        for d in deps:
            j = find(d, tasklist)
            # print("Dep %s(%i) --> %s(%i)\n %s --> %s" %(task[i].label, i, d, j, task[i], task[j]))
            if task[i].x < task[j].x + task[j].dur:
                task[i].x = task[j].x + task[j].dur
                # print("updated", d, task[i], task[j])
                flag = True

        if flag:
            i = 0
        else:
            i += 1

        nloop += 1

    if nloop == maxLoop:
        print("Max loops exceeded")

    tasklist = sorted(tasklist, key=lambda x: x.x)
    return tasklist


def optimize(tasklist):
    for i in range(len(tasklist)):
        taski = tasklist[i]
        x0 = taski.startAfter

        for j in range(i):
            taskj = tasklist[j]
            if (taskj.label in taski.depend) or \
               (taskj.user == taski.user):
                    x0 = max(x0, taskj.x + taskj.dur)
        tasklist[i].x = x0

        if tasklist[i].x > tasklist[i].startBy:
            print("Project %i will be late! (%s)" %(i, taski))

    return tasklist


def find(label, tasklist):
    for i in range(len(tasklist)):
        if tasklist[i].label == label:
            return i

    raise ValueError("label '%s' not found" %(label))


