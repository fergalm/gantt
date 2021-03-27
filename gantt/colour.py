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


class ColourBy():
    def __init__(self, tasklist, cmap=plt.cm.rainbow):
        self.userdict = self.compute_user_dict(tasklist, cmap)

    def __call__(self):
        return 'w', 'k'

    def compute_user_dict(self, tasklist, cmap):
        self.userdict = dict()

        values = self.compute_colour_values(tasklist)
        nVals = float(len(values)) - 1
        nVals = max(nVals, 1)

        for i, u in enumerate(values):
            index = i / nVals
            colour = cmap(index)
            self.userdict[u] = colour
        return self.userdict

    def legend(self, **kwargs):

        xlim = plt.xlim()
        handles = []
        labels = []

        for k in self.userdict:
            h = plt.plot(0, 0, 's', color=self.userdict[k])[0]
            h.set_visible(True)
            handles.append(h)
            labels.append(k)

        plt.legend(handles, labels, **kwargs)
        plt.xlim(xlim)

class ColourByUser(ColourBy):
    def __call__(self, task):
        user = task.user
        fc = self.userdict[user]
        ec = 'grey'
        return fc, ec

    def compute_colour_values(self, tasklist):
        return set(map(lambda x: x.user, tasklist))



class ColourByDuration(ColourBy):

    def __call__(self, task):
        user = task.dur
        fc = self.userdict[user]
        ec = 'grey'
        return fc, ec

    def compute_colour_values(self, tasklist):
        return set(map(lambda x: x.dur, tasklist))


class ColourByStartDate(ColourBy):
    def __call__(self, task):
        key = task.x
        fc = self.userdict[key]
        ec = 'grey'
        return fc, ec

    def compute_colour_values(self, tasklist):
        return set(map(lambda x: x.x, tasklist))
