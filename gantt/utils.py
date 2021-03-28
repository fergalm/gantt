import pandas as pd

def find(label, tasklist):
    for i in range(len(tasklist)):
        if tasklist[i].label == label:
            return i

    #I've turned this off because the weekend markers were raising errors.
    #raise ValueError("label '%s' not found" %(label))
    return None

def to_mjd(date):
    date = pd.to_datetime(date)
    jd = date.to_julian_date()
    return jd - 2_400_000.5

    
def from_mjd(mjd):
    jd = mjd + 2_400_000.5
    date = pd.to_datetime(jd, origin='julian', unit='D')
    return date
