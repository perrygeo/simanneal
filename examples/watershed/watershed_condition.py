import math
import sys
import os
sys.path.append(os.path.abspath('../'))
from anneal import Annealer
import shapefile

import random

#-----------------------------------------------#
#-------------- Configuration ------------------#
#-----------------------------------------------#
shp = './data/huc6_4326.shp'

species = ['StlHd_m', 'Coho_m', 'Chnk_m']

targets = { 
            'StlHd_m': 511000, 
            'Coho_m': 521000, 
            'Chnk_m': 551000 
          }

# Note that these values will be added to watershed cost
# if the solution fails to meet targets
# the total cost of a solution thus depends on watershed cost
# plus all penalties. 
penalties = { 
              'StlHd_m': 500, 
              'Coho_m': 400, 
              'Chnk_m': 300 
            }

costs = ['pcp80bdfmm', ]
uidfield = 'OBJECTID'
NUMREPS = 20 
NUMITER = 30000

# Uncomment to manually define temperature schedule
# Otherwise, optimal schedule will be calculated 
# 
# SCHEDULE = {'tmin': 10, 'tmax': 6500, 'steps': 1}

#-----------------------------------------------#

watersheds = {}

def field_by_num(fieldname, fields):
    fnames = [x[0] for x in fields]
    return fnames.index(fieldname) - 1

print "Loading data from shapefile..."
sf = shapefile.Reader(shp)
fields = sf.fields
for rec in sf.records():
    skip = False
    vals = {}
    for s in species:
        vals[s] = rec[field_by_num(s, fields)]
    # precalc costs
    watershed_cost = 0
    for c in costs:
        fnum = field_by_num(c, fields)
        watershed_cost += rec[fnum]

    vals['watershed_cost'] = watershed_cost

    if watershed_cost < 0.00001:
        skip = True

    if not skip:
        watersheds[int(rec[field_by_num(uidfield, fields)])] = vals

    # At this point, the `watersheds`variable should be a dictionary of watersheds
    # where each watershed value is a dictionary of species and costs, e.g.
    # {171003030703: {'Chnk_m': 11223.5, 'StlHd_m': 12263.7, 'Coho_m': 11359.1, 'watershed_cost': 1234}, 

hucs = watersheds.keys()
num_hucs = len(hucs)

def run(schedule=None):
    state = []

    def reserve_move(state):
        """
        Select random watershed
        then
        Add watershed (if not already in state) OR remove it. 
        * This is the Marxan technique as well
        """
        huc = hucs[int(random.random() * num_hucs)]
        #huc = hucs[random.randint(0,num_hucs-1)]

        if huc in state:
            state.remove(huc)
        else:
            state.append(huc)

    def reserve_energy(state):
        """
        The "Objective Function"...
        Calculates the 'energy' of the reserve.
        Should incorporate costs of reserve and penalties 
        for not meeting species targets. 

        Note: This example is extremely simplistic compared to 
        the Marxan objective function (see Appendix B in Marxan manual)
        but at least we have access to it!
        """
        # Initialize variables
        energy = 0
        totals = {}
        for fish in species:
            totals[fish] = 0

        # Get total cost and habitat in current state
        for huc in state:
            watershed = watersheds[huc]
            # Sum up total habitat for each fish
            for fish in species:
                if energy == 0:
                    # reset for new calcs ie first watershed
                    totals[fish] = watershed[fish]
                else:
                    # add for additional watersheds
                    totals[fish] += watershed[fish]

            # Incorporate Cost of including watershed
            energy += watershed['watershed_cost']

        # incorporate penalties for missing species targets
        for fish in species:
            pct = totals[fish] / targets[fish]
            if pct < 1.0: # if missed target, ie total < target
                if pct < 0.1:
                    # Avoid zerodivision errors 
                    # Limits the final to 10x specified penalty
                    pct = 0.1
                penalty = int(penalties[fish] / pct)
                energy += penalty 
        
        return energy

    annealer = Annealer(reserve_energy, reserve_move)
    if schedule is None:
       print '----\nAutomatically determining optimal temperature schedule'
       schedule = annealer.auto(state, minutes=6)

    try:
        schedule['steps'] = NUMITER
    except:
        pass # just keep the auto one

    print '---\nAnnealing from %.2f to %.2f over %i steps:' % (schedule['tmax'], 
            schedule['tmin'], schedule['steps'])

    state, e = annealer.anneal(state, schedule['tmax'], schedule['tmin'], 
                               schedule['steps'], updates=6)

    print "Reserve cost = %r" % reserve_energy(state)
    state.sort()
    for watershed in state:
        print "\t", watershed, watersheds[watershed]
    return state, reserve_energy(state), schedule

if __name__ == "__main__":
    freq = {}
    states = []
    try:
        schedule = SCHEDULE
    except:
        schedule = None
    for i in range(NUMREPS):
        state, energy, schedule = run(schedule)
        states.append((state, energy))
        for w in state:
            if freq.has_key(w):
                freq[w] += 1
            else:
                freq[w] = 1

    print 
    print "States"
    for s in states:
        print s
    print 
    print "Frequency of hit (max of %s reps)..." % NUMREPS
    ks = freq.keys()
    ks.sort()
    for k in ks:
        v = freq[k]
        print k, "#"*int(v), v
