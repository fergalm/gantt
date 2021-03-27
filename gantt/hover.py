
"""
Show an tooltip
"""

from ipdb import set_trace as idebug
import matplotlib.pyplot as plt

import gantt.utils as utils

artists = []


class Interact():
    def __init__(self, tasklist):
        self.tasklist = tasklist
        self.artists = []
        self.fig = plt.gcf()
        self.fig.canvas.mpl_connect('motion_notify_event', self.hover)
        print("connected")

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        self.fig.canvas.mpl_disconnect('motion_notify_event')

    def __call__(self, event):
        self.hover(event)

    def hover(self, event):
        ax = plt.gca()
        flag = False
        for curve in ax.get_children():
            # Searching which data member corresponds to current mouse position
            if curve.contains(event)[0]:
                label = curve.get_label()
                if isinstance(label, str) and len(label) > 0 and label[0] != '_':
                    self.clear_artists()
                    self.update_tooltip(event, label)
                    self.highlight_dependencies(event, label)
                    flag = True
        if not flag:
            self.clear_artists()

    def clear_artists(self):
        while len(self.artists) >0:
            x = self.artists.pop()
            x.set_visible(False)
            del x

    def update_tooltip(self, event, label):
        wh = utils.find(label, self.tasklist)
        if wh is None:
            return 
        
        task = self.tasklist[wh]

        x, y = event.xdata, event.ydata
        label = "%s %s\n%s" %(task.label, task.user, task.description)
        tooltip = plt.gca().annotate(label, xy=(x,y),
                xytext=(-0, +10),
                xycoords='data',
                textcoords="offset points",
                bbox=dict(boxstyle='round', fc='w'),
                arrowprops=dict(arrowstyle="->"))

        plt.gcf().canvas.draw_idle()
        self.artists.append(tooltip)

    def highlight_dependencies(self, event, label):
        deps = self.find_dependencies(label)

        for d in deps:
            self.mark_task(d)

    def find_dependencies(self, label):

        deps = []
        i = utils.find(label, self.tasklist)
        if i is not None:
            t0 = self.tasklist[i]
            deps.extend(t0.depend)

        i = 0
        while i < len(deps):
            t = utils.find(deps[i], self.tasklist)
            depTask = self.tasklist[t]
            subDepend = depTask.depend

            for s in subDepend:
                if s not in deps:
                    deps.append(s)

            # print(i, depTask.label, deps)
            i+= 1

        return deps

    def mark_task(self, label):
        index = utils.find(label, self.tasklist)
        task = self.tasklist[index]

        x1 = task.start_date
        width = task.end_date - x1
        y1 = len(self.tasklist) - index - .2
        height = .4

        box = plt.Rectangle((x1, y1), width, height, fill=False, lw=4, color='k')
        plt.gca().add_artist(box)
        self.artists.append(box)


# def activate_tooltips():
#     fig = plt.gcf()
#     fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)


# def on_plot_hover(event):
#     ax = plt.gca()
#     # Iterating over each data member plotted
#     for curve in ax.get_lines():
#         # Searching which data member corresponds to current mouse position
#         if curve.contains(event)[0]:
#             label = curve.get_label()
#             if label[0] != '_':
#                 clear_artists()

#                 newtip = update_tooltip(event.xdata, event.ydata, label)
#                 artists.append(newtip)


# def clear_artists():



# def update_tooltip( x, y, label):

#     tooltip = plt.gca().annotate(label, xy=(x,y),
#             xytext=(-0, -0),
#             xycoords='data',
#             textcoords="offset points",
#             bbox=dict(boxstyle='round', fc='w'),
#             arrowprops=dict(arrowstyle="->"))

#     plt.gcf().canvas.draw_idle()
#     return tooltip


# def getAllDependencies(task, tasklist):
#     deps = []
#     deps.extend(task.depend)

#     i = 0
#     while i < len(deps):
#         t = utils.find(deps[i], tasklist)
#         depTask = tasklist[t]
#         subDepend = depTask.depend

#         for s in subDepend:
#             if s not in deps:
#                 deps.append(s)

#         print(i, depTask.label, deps)
#         i+= 1

#     return deps
