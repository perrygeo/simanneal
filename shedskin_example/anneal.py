#!/usr/bin/env python
# Python module for simulated annealing - anneal.py - v1.0 - 2 Sep 2009
#
# Copyright (c) 2009, Richard J. Wagner <wagnerr@umich.edu>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
This module performs simulated annealing to find a state of a system that
minimizes its energy.

An example program demonstrates simulated annealing with a traveling
salesman problem to find the shortest route to visit the twenty largest
cities in the United States.

Notes:
    Matt Perry 6/24/12
        Changed to slicing lists instead of deepcopy-ing them.
        e.g. state = prevState[:] instead of state = deepcopy(prevState)
        Huge performance enhancement (~5-10x faster)
        Should be identical behavior if the items in the state list are immutable.
        (immutable objects include integers and strings so should be safe)
"""

# How to optimize a system with simulated annealing:
#
# 1) Define a format for describing the state of the system.
#
# 2) Define a function to calculate the energy of a state.
#
# 3) Define a function to make a random change to a state.
#
# 4) Choose a maximum temperature, minimum temperature, and number of steps.
#
# 5) Set the annealer to work with your state and functions.
#
# 6) Study the variation in energy with temperature and duration to find a
# productive annealing schedule.
#
# Or,
#
# 4) Run the automatic annealer which will attempt to choose reasonable values
# for maximum and minimum temperatures and then anneal for the allotted time.

import math
import sys
import time
import random


def time_string(seconds):
    """Returns time in seconds as a string formatted HHHH:MM:SS."""
    s = int(round(seconds))  # round to nearest second
    h, s = divmod(s, 3600)   # get hours and remainder
    m, s = divmod(s, 60)     # split remainder into minutes and seconds
    return '%4i:%02i:%02i' % (h, m, s)


def update(T, E, acceptance, improvement, step, steps, start):
    """Prints the current temperature, energy, acceptance rate,
    improvement rate, elapsed time, and remaining time.

    The acceptance rate indicates the percentage of moves since the last
    update that were accepted by the Metropolis algorithm.  It includes
    moves that decreased the energy, moves that left the energy
    unchanged, and moves that increased the energy yet were reached by
    thermal excitation.

    The improvement rate indicates the percentage of moves since the
    last update that strictly decreased the energy.  At high
    temperatures it will include both moves that improved the overall
    state and moves that simply undid previously accepted moves that
    increased the energy by thermal excititation.  At low temperatures
    it will tend toward zero as the moves that can decrease the energy
    are exhausted and moves that would increase the energy are no longer
    thermally accessible."""

    elapsed = time.time() - start
    if step == 0:
        print ' Temperature        Energy    Accept   Improve     Elapsed   Remaining'
        print '%12.2f  %12.2f                      %s            ' % \
            (T, E, time_string(elapsed))
    else:
        remain = (steps - step) * (elapsed / step)
        print '%12.2f  %12.2f  %7.2f%%  %7.2f%%  %s  %s' % \
            (T, E, 100.0 * acceptance, 100.0 * improvement,
                time_string(elapsed), time_string(remain))


def anneal(state, Tmax, Tmin, steps, updates=0):
    """Minimizes the energy of a system by simulated annealing.

    Keyword arguments:
    state -- an initial arrangement of the system
    Tmax -- maximum temperature (in units of energy)
    Tmin -- minimum temperature (must be greater than zero)
    steps -- the number of steps requested
    updates -- the number of updates to print during annealing

    Returns the best state and energy found."""

    step = 0
    steps = float(steps)
    start = time.time()

    # Precompute factor for exponential cooling from Tmax to Tmin
    if Tmin <= 0.0:
        print 'Exponential cooling requires a minimum temperature greater than zero.'
        sys.exit()
    Tfactor = -math.log(float(Tmax) / Tmin)

    # Note initial state
    T = Tmax
    E = energy(state)
    # prevState = copy.deepcopy(state)
    prevState = state[:]
    prevEnergy = E
    # bestState = copy.deepcopy(state)
    bestState = state[:]
    bestEnergy = E
    trials, accepts, improves = 0.0, 0.0, 0.0
    if updates > 0:
        updateWavelength = steps / updates
        update(T, E, 0, 0, step, steps, start)

    # Attempt moves to new states
    while step < steps:
        step += 1
        T = Tmax * math.exp(Tfactor * step / steps)
        move(state)
        E = energy(state)
        dE = E - prevEnergy
        trials += 1
        if dE > 0.0 and math.exp(-dE / T) < random.random():
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
        if updates > 1:
            if step // updateWavelength > (step - 1) // updateWavelength:
                update(T, E, accepts / trials, improves / trials, step, steps, start)
                trials, accepts, improves = 0.0, 0.0, 0.0

    # Return best state and energy
    return bestState, bestEnergy


##############################################################################
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

from data import watersheds

hucs = watersheds.keys()
num_hucs = len(hucs)

def move(state):
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

def energy(state):
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

if __name__ == '__main__':
    """Test annealer with a traveling salesman problem."""

    state = []

    new_state, e = anneal(state, 100000, 4, 1000000)

    new_state.sort()
    print "['103225', '103386', '103470', '103633', '103650', '103653', '103665', '95534']" 
    print "^^^^^ previously ^^^"
    print new_state
