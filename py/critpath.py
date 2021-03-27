# -*- coding: utf-8 -*-
"""
Created on Mon May 25 21:25:23 2020

A chain is a 3 tuple representing all the direct and indirect dependencies
of a task. The elements are
( Label_of_task,
  List of tasks in dependency chain, starting with earliest task, and ending
          with the listed task,
  Duration of all tasks in the chain
)

A chainList is a list of such chains. If a task has two dependencies (eg
A and B must be complete before C can be started) it will appear
in the chain list twice
[
     (C, [A, C], 2),
     (C, [B, C], 13)
]


@author: fergal
"""

from ipdb import set_trace as idebug
from pprint import pprint

def sortByCriticalPath(tasklist):
    """

    Returns `tasklist`, ordered so tasks are sorted first
    by the length of the longest dependency group they belogn to,
    and then by where they sit inside that dependency group.

    Returns
    ---------
    outlist, a resorted version of tasklist
    """
    chainList = findChains(tasklist)
    outlist = orderTasksByCritPath(tasklist, chainList)
    return outlist



def findChains(tasklist):
    """Scan through every element of tasklist, and find all the chains"""
    #TODO It would be great if this function could remember the chain
    #for a previously encountered task, to save time.

    out = []
    for t in tasklist:
        out.extend( process(t, tasklist))
    chainList = sorted(out, key=lambda x: x[-1], reverse=True)
    return chainList


def orderTasksByCritPath(tasklist, chainList):
    outlist = []
    visited = dict()

    # pprint(chainList)
    for chain in chainList:
        depTree = chain[1]
        for i in range(len(depTree)):
            # print("***")
            # pprint(outlist)
            task = find(depTree[i], tasklist)
            task = tasklist[task]

            # if task.label == "DS-501d":
                # idebug()

            if task in visited:
                continue

            subsequentDependencies = depTree[i+1:]
            for j in range(len(outlist)):
                if outlist[j].label in subsequentDependencies:
                    outlist.insert(j, task)
                    visited[task] = True
                    break

            #If we haven't added the task yet, it is not a dependency of
            #any previously scheduled task. Add it to the end of the list
            if not task in visited:
                #outlist.insert(0, task )
                outlist.append(task)
                visited[task] = True
    return outlist




# def sortTasksByChainLength(tasklist, chainList):
#     """Do the sorting"""
#     outlist = []
#     visited = dict()

#     pprint(chainList)
#     # idebug()

#     for chain in chainList:
#         depTree = chain[1]
#         for label in depTree:
#             if label in visited:
#                 continue
#             visited[label] = True
#             i = find(label, tasklist)
#             outlist.append(tasklist[i])
#             pprint(outlist)
#             idebug()
#     return outlist


def process(task, tasklist):
    """The main function.

    Given a task, figure out all the dependency chains for a task


    a___
        |_e_
    b___|   |
            |__g
    c___    |
        |_f_|
    d___|

    This diagram includes the chains
    gea
    geb
    gfc
    gfd
    ea
    eb
    ...
    c
    d
    """

    duration = task.dur
    label = task.label
    deps = task.depend

    #No deps => This is a starting node of the project
    if len(deps) == 0:
        return [(label, [label], duration)]

    out = []
    # idebug()
    for d in deps:
        i= find(d, tasklist)
        taski = tasklist[i]
        chainList = process(taski, tasklist)
        for chain in chainList:
            newChain = addTaskToChain(task, chain)
            out.append(newChain)
        # print(chainList)
        # print(out)
        # idebug()
    return out


def addTaskToChain(task, chain):
    label = task.label
    dur = task.dur
    newChain = (label, chain[1] + [label] , dur + chain[2])
    return newChain



#TODO This function is duplicated
def find(label, tasklist):
    for i in range(len(tasklist)):
        if tasklist[i].label == label:
            return i

    raise ValueError("label '%s' not found" %(label))
