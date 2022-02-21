# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 07:00:28 2022

TODO

1. start_date = day1 + pd.to_timedelta(task[i].x)  Nice and simple
2. Calendar dates


@author: fergal
"""

from ipdb import set_trace as idebug
import pandas as pd
import numpy as np
import mip

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


def main(fn, day1):
    tasklist = loadTable(fn)

    day1 = pd.to_datetime(day1)
    verifyInputs(tasklist, day1)
    depends, assigns, duration = parseInputs(tasklist)

    print(depends)
    #return 
    model = create_model(assigns, depends, duration)
    model = set_dependency_constraints(model, duration, depends)
    model = set_assignment_contraints(model, duration, assigns)
    model = set_date_constraints(model, day1, tasklist)

    #Set the objective
    last_task = model.var_by_name("start%i" %(len(tasklist) - 1))
    model.objective = mip.minimize(last_task)
    model.optimize()
    #Check for convergence!

    updateTaskList(tasklist, model, day1)
    textReport(tasklist, "label")



def verifyInputs(tasklist, day1):
    return True


def parseInputs(tasklist):
    """Create the input data for the MILP solver"""
    label_dict = createTaskLabelDict(tasklist)
    workers = createWorkerDict(tasklist)

    numTask = len(tasklist)
    numWorker = len(workers)

    depends = np.zeros((numTask, numTask),dtype=bool)
    assigns = np.zeros((numTask, numWorker), dtype=bool)
    durations = np.zeros(numTask, dtype=float)

    for i in range(numTask):
        for dependency in tasklist[i].depend:
            if dependency == 0:
                continue 

            j = label_dict[dependency]
            depends[i, j] = True

        workerNum = workers[tasklist[i].user]
        assigns[i, workerNum] = True

        durations[i] = tasklist[i].dur
    return depends, assigns, durations


def createTaskLabelDict(tasklist):
    out = dict()
    for i, task in enumerate(tasklist):
        out[task.label] = i
    return out

def create_model(depend, assigns, duration):
    nTask = len(duration)
    model = mip.Model("gantt")
    [model.add_var(name=f"start{i}", lb=0) for i in range(nTask)]
    return model


def set_dependency_constraints(model, duration, depends):
    nTask = len(duration)

    start = []
    for i in range(nTask):
        start.append( model.var_by_name(f"start{i}"))

    #Set task order contraints
    for i in range(nTask):
        for j in range(nTask):
            # If Task i depends task j
            if depends[i, j]:
                model += (start[i] - start[j] - duration[j]) >= 0
    return model


def set_assignment_contraints(model, duration, assigns):
    """Set assignment based contraints:
        No worker doing two things at the same time
    """
    nTask, nWorker = assigns.shape

    start = []
    for i in range(nTask):
        start.append( model.var_by_name(f"start{i}"))

    huge = 2 * np.sum(duration)  #No task will start after this time
    for i in range(nTask):
        for j in range(i+1, nTask):
            for k in range(nWorker):
                if assigns[i, k] & assigns[j, k] :
                    #r is a dummy variable that ensures only one of the next
                    #two constraints is imposed. It acts like an OR switch
                    r = model.add_var(name=f"OR switch {i},{j},{k}", var_type=mip.BINARY)
                    #Task j ends before task i starts OR
                    #Task j starts after task i ends
                    model += (start[j] + duration[j] - start[i]) <=  (1-r) * huge
                    model += (start[j] - duration[i] - start[i]) >=  r * huge
    return model


def createWorkerDict(tasklist):
    workers = dict()
    w = 0
    for task in tasklist:
        if task.user not in workers:
            workers[task.user] = w
            w += 1
    return workers



def updateTaskList(tasklist, model, day1):
    bd = pd.tseries.offsets.BusinessDay()

    num_day = int(np.max(npmap(lambda x: x.x + x.dur, tasklist)))
    day2 = day1 + num_day * bd
    bday = pd.bdate_range(day1, day2)
    for i in range(len(tasklist)):
        day_num = model.var_by_name(f"start{i}").x
        tasklist[i].x = day_num
        tasklist[i].business_day = bday[ int(day_num) ]


def set_date_constraints(model, day1, tasklist):
    for i, task in enumerate(tasklist):
        var = model.var_by_name( f"start{i}")

        if task.startAfter is not None:
            t1 = pd.to_datetime(task.startAfter)
            ndays = len(pd.bdate_range(day1, t1))
            model += var >= ndays

        if task.startBy is not None:
            t1 = pd.to_datetime(task.startBy)
            ndays = len(pd.bdate_range(day1, t1))
            model += var <= ndays
    return model


def textReport(tasklist, sortkey, clrKey=None):
    #Or some such
    sortlist = sorted(tasklist, key =lambda x: getattr(x, sortkey))

    for task in sortlist:
        datestr = task.business_day.strftime("%Y-%m-%d") 
        datestr += " (%i)" %(task.x)
        print("%s %10s %40s %3i" 
            %(datestr, task.label, task.description[:40], task.dur))


def loadTable(fn):
    """
    TODO
    ------
    o convert this to accept dates, not relative day numbers
    o Deal with whitespace in dependency list"""
    df = pd.read_csv(fn)
    bd = pd.tseries.offsets.BusinessDay()


    tasklist = []

    x0 = 0
    for i, row in df.iterrows():
        if np.isnan(row.Duration):
            row.Duration = "1"
        row.Duration = float(row.Duration)

        if isinstance(row.Dependencies, float) and np.isnan(row.Dependencies):
            depend = []
        else:
            depend = row.Dependencies.split(',')

        if  not isinstance(row.StartAfter, str):
            row.StartAfter = None

        if isinstance(row.EndBy, str):
            startBy = pd.to_datetime(row.EndBy) - int(row.Duration) * bd
        else:
            startBy = None

#        if np.isnan(row.EndBy):
#            row.EndBy= np.inf
#        startBy = float(row.EndBy) - float(row.Duration)

        # idebug()
        t = Task(label = row.Label, \
                 description = row.Description, \
                 dur = float(row.Duration), \
                 user = row.Assignee, \
                 depend = depend, \
                 startAfter = row.StartAfter, \
                 startBy = startBy,\
                 x = x0,
                 )
        tasklist.append(t)

        x0 += t.dur

    return tasklist

def npmap(function, *array):
    """Perform a map, and package the result into an np array"""
    return np.array( lmap(function, *array))

def lmap(function, *array):
    """Perform a map, and package the result into a list, like what map did in Py2.7"""
    return list(map(function, *array))    
