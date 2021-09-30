
"""

I have N tasks and W workers

Each task has a start time, t_i, duration tau_i.
The durations are inputs, the t_i's are sought.

There are a couple of constraints when each task can be computed.

1. There exists a matrix of dependencies D. If d_ij is true, then task i depends on task j, and must not start until task j is complete.

2. Each task t_i can be completed by one and only one worker. If
w_ij is true then task i must be completed by worker j. \sum_j w_ij == 1 for all i. This constraint is a precondition.

3. A worker may be able to work on more than one task, but only one at a time.

I want to organise the tasks so they are completed in the shortest time possible:

In mathmatics I want to 
minimize max(t_i + tau_i)

Subject the constraints 
(1) d_ij * (t_i - t_j - tau_j) >= 0  for all i, j
(3) p_ik * p_jk * (t_j + tau_j - t_i) * (t_j - tau_i - t_i) <= 0

(if worker k is going to perform tasks i and j then they do not overlap in time)


#####
TODO 
1. Exhaustively check task dependencies for loops
1  What's a better objective? Adding a dummy "finish" task of 0 duration, or 
   optimising the sum of the finish times?
2. Convert a spreadsheet to 'dependency' and 'worker' matrices
3. Add ability to set must-start-after and must-end-by dates (lb and ub on "start" vars)
4. Convert business date <--> interger days
5. Plotting of results
"""

import numpy as np
import mip 

def main():
    
    """ Logic to prevent multiple workers is commented out right now
    because it isn't working yet
    """
    
    nTask = 5
    nWorker = 2
    duration = [10,11,12,13,14]
    
    #Dependency Tree looks like
    # 0 -- 2 -- 4
    #      3 ---|
    # 1 ---|
    depends = np.zeros((nTask,nTask), dtype=bool) 
    depends[2, 0] = True 
    depends[3, 1] = True  
    depends[4, 2] = True  
    depends[4, 3] = True 
    
    #depends[3,2] = True  #Make task 3 depend on task 2, stretching out the timeline
    verify_dependency_graph(depends) 
    
    assigns = np.zeros((nTask, nWorker), dtype=bool)
    #assign tasks to workers in alternating order
    assigns[0, 0] = True
    assigns[1, 1] = True
    assigns[2, 0] = True
    assigns[3, 1] = True
    assigns[4, 0] = True
    verify_task_assignments(assigns)
    
    return solve(depends, assigns, duration)

def solve(depends, assigns, duration):
    nTask, nWorker = assigns.shape
    
    model = mip.Model("gantt")
    start = [model.add_var(name=f"start task {i}", lb=0) for i in range(nTask)]
 
    #Set task order contraints
    for i in range(nTask):
        for j in range(nTask):
            name = "Task i depends task j"
            if depends[i, j]:
                model += (start[i] - start[j] - duration[j]) >= 0


    #Set assignment based contraints: No worker doing two things at the same time
    huge = 2 * np.sum(duration)  #No task will start after this time
    for i in range(nTask):
        for j in range(i+1, nTask):
            for k in range(nWorker):
                if assigns[i, k] & assigns[j, k] :
                    #r is a dummy variable that ensures only one of the next
                    #two constraints is imposed. It acts like an OR switch
                    r = model.add_var(name=f"OR switch {i},{j},{k}", var_type=mip.BINARY)
                    #Task j ends before task i starts OR
                    model += (start[j] + duration[j] - start[i]) <=  (1-r) * huge
                    #Task j starts after task i ends
                    model += (start[j] - duration[i] - start[i]) >=  r * huge

    #Set the objective
    model.objective = mip.minimize(start[-1])
    opt = model.optimize(max_seconds=20)
    print(opt)
    print(list(map(lambda i: model.vars[i].x, range(nTask))))
    return model


#pass
#print(i, j, k)
#print(f"model += (start[{j}] + duration[{j}] - start[{i}]) >= 0")
#print(f"model += (start[{j}] - duration[{i}] - start[{i}]) <= 0")
    
def verify_dependency_graph(depends):
    
    #If task i depends on task j, task j can't depend on task i
    #todo, generalise this for loops of arbitrary length
    assert np.all( ~ (depends & depends.transpose()) ), depends

    
def verify_task_assignments(assigns):
    #Each task assigned to one and only one person
    assert np.all(np.sum(assigns, axis=0)) == 1 
