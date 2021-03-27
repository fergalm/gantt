
def find(label, tasklist):
    for i in range(len(tasklist)):
        if tasklist[i].label == label:
            return i

    raise ValueError("label '%s' not found" %(label))


