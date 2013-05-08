#!/usr/bin/env python
#TODO replace header

from libc cimport math
from numpy import random
cimport numpy as np
cimport cython

ctypedef np.int_t DTYPE_t

@cython.boundscheck(False)
def anneal(list state, double Tmax, double Tmin, unsigned int steps):
    """Minimizes the energy of a system by simulated annealing.

    Keyword arguments:
    state -- an initial arrangement of the system
    Tmax -- maximum temperature (in units of energy)
    Tmin -- minimum temperature (must be greater than zero)
    steps -- the number of steps requested

    Returns the best state and energy found."""

    cdef unsigned int step, trails, accepts, improves
    cdef double T, E, prevEnergy, bestEnergy, Tfactor
    cdef list prevState, bestState

    step = 0

    # Precompute factor for exponential cooling from Tmax to Tmin
    if Tmin <= 0.0:
        print 'Exponential cooling requires a minimum temperature greater than zero.'
        Tmin = 1.0
    Tfactor = -1.0 * math.log(Tmax / Tmin)

    # Note initial state
    T = Tmax
    E = energy(state)
    # prevState = copy.deepcopy(state)
    prevState = state[:]
    prevEnergy = E
    # bestState = copy.deepcopy(state)
    bestState = state[:]
    bestEnergy = E
    trials, accepts, improves = 0, 0, 0

    # pregenerate random numbers
    ###################################################
    cdef np.ndarray[int, ndim=1] rand_hucids = random.random_integers(0, len(units)-1, size=steps+1)
    ###################################################
    cdef np.ndarray[double, ndim=1] rand_nums = random.rand(steps+1)

    # Attempt moves to new states
    while step < steps:
        step += 1
        T = Tmax * math.exp(Tfactor * step / steps)

        ###################################################
        #  move()
        """
        Select random watershed
        then
        Add watershed (if not already in state) OR remove it. 
        * This is the Marxan technique as well
        """
        unit = units[rand_unitids[step]]

        if unit in state:
            state.remove(unit)
        else:
            state.append(unit)
        ###################################################
        E = energy(state)
        dE = E - prevEnergy
        trials += 1
        if dE > 0.0 and math.exp(-dE / T) < rand_nums[step]:
            # Restore previous state
            # state = copy.deepcopy(prevState)
            state = prevState[:]
            E = prevEnergy
        else:
            # Accept new state and compare to best state
            accepts += 1
            if dE < 0.0:
                improves += 1
            # prevState = copy.deepcopy(state)
            prevState = state[:]
            prevEnergy = E
            if E < bestEnergy:
                # bestState = copy.deepcopy(state)
                bestState = state[:]
                bestEnergy = E

    # Return best state and energy
    return bestState, bestEnergy


##############################################################################
cdef list species
cdef list hucs
cdef unsigned int num_hucs

species = ['StlHd_m', 'Coho_m', 'Chnk_m']
targets = {
    'StlHd_m': 511000,
    'Coho_m': 521000,
    'Chnk_m': 551000
}
penalties = {
    'StlHd_m': 500,
    'Coho_m': 400,
    'Chnk_m': 300
}
costs = ['pcp80bdfmm', ]
uidfield = 'OBJECTID'

from data import watersheds

hucs = watersheds.keys()
num_hucs = len(hucs)



cdef energy(list state):
    """
    The "Objective Function"...
    Calculates the 'energy' of the reserve.
    Should incorporate costs of reserve and penalties
    for not meeting species targets.

    Note:
        This example is extremely simplistic compared to
    the Marxan objective function (see Appendix B in Marxan manual)
    but at least we have access to it!
    """
    # Initialize variables
    cdef double energy, pct, penalty

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
            penalty = penalties[fish] / pct
            energy += penalty 
    
    return energy
