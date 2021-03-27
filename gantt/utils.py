
def find(label, tasklist):
    for i in range(len(tasklist)):
        if tasklist[i].label == label:
            return i

    #I've turned this off because the weekend markers were raising errors.
    #raise ValueError("label '%s' not found" %(label))
    return None

