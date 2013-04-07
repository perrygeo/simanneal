# Python module for simulated annealing

This module performs [simulated annealing optimization](http://en.wikipedia.org/wiki/Simulated_annealing) to find a state of a system that minimizes its energy.

Simulated annealing is used to find a close-to-optimal solution amongst an extremely large (but finite) set of potential solutions. The process involves::

1. A random _move_  altering the state 
2. Assess the _energy_ of the new state using an objective metric
3. Compare the energy to the previous state and 
   decide whether to accept the new solution or
   reject it. 
4. Repeat until you have converged on an acceptable answer


For a state to be accepted, it must either be a drop in energy (i.e. an improvement in the objective metric) or 
it must be within the bounds of the current "temperature"; increasing energy is accepted to a 
lesser extent as the process goes on. In this way, we avoid getting trapped by "local minima" early in the process.  

From the [British Journal of Radiology](http://bjr.birjournals.org/content/76/910/678/F6.expansion.html)
![BJR](http://bjr.birjournals.org/content/76/910/678/F6.medium.gif)


Think of traveling from the top of a mountain to the ocean - even though your goal is to drop to sea level, you may have to climb some small inclines along the way in order to get there.

Simulated annealing is inspired by the mettalurgic process of annealing whereby metals must be cooled at a regular schedule in order to settle into their lowest energy state. 

## Theoretical Example

Let's say you want to buy up some land to save your favorite creatures from development pressures.
You create a list of species, each with a specific conservation target: 
We want to conserve at least 200 acres of beaver habitat, 400 acres of snowy plover habitat, etc.

There are 100 parcels for sale in the area. You want to buy up a number of parcels to meet your conservation
targets but want to do so at the lowest possible cost.

If you had a few parcels in mind, you could potentially calculate all the possible combinations but, with 100 parcels, there are 9.3326215444×10<sup>157</sup> combinations! So that's where simulated annealing helps.

You could write an objective function to calculate the "energy" for each possible solution ("Total cost of all included parcels plus a penalty for any conservation targets that were missed") and a 
function to randomly "move" the state ("Randomly add or remove a property from the set") and you could then run simulated annealing to go through the solution space and converge on the optimal set of parcels that would have the lowest "energy" (i.e. the set of parcels that met the most of your conservation objectives with the lowest cost)


## How to optimize a system with simulated annealing:
 
Define a format for describing the state of the system.

```
all_parcels = [745, 234, ...]
state = []  # a list of parcel ids; a subset of all_parcels
```

Define a function to calculate the energy of a state.

```
def energy(state):
    """
    The objective Function... calculates the 'energy' of the state
    Incorporate costs and penalties for not meeting species targets. 
    """

    energy = sum([get_cost(parcel) for parcel in state])

    for s in species:
        if pct < 1.0: # if missed target, ie total < target
            energy += get_penalty(s)
    
    return energy
```

Define a function to make a random change to a state.

```
def move(state):
    """ 
    Select random parcel
    then add parcel OR remove it. 
    """
    huc = random.choice(all_parcels)

    if huc in state:
        state.remove(huc)
    else:
        state.append(huc)
```
 
Run the automatic annealer which will attempt to choose reasonable values
    for maximum and minimum temperatures and then anneal the solution.

```
from anneal import Annealer
annealer = Annealer(energy, move)
schedule = annealer.auto(state, minutes=1)
state, e = annealer.anneal(state, schedule['tmax'], schedule['tmin'], 
                            schedule['steps'], updates=6)
print state  # the "final" solution
```


For a working example similar to the conservation problem described above, see the `example/` directory.

## Notes

1. Thanks to Richard J. Wagner at University of Michigan for writing and contributing the bulk of this code.
2. Some effort has been made to increase performance but this is nowhere near as fast as optimized solutions written in other low-level languages. On the other hand, this is a very flexible, Python-based solution that can be used for rapidly 
experimenting with a computational problem with minimal overhead. 
3. Using PyPy instead of CPython can yield substantial increases in performance.
4. For true conservation planning, it is probably best to use [Marxan](http://www.uq.edu.au/marxan/) which has been optimized and designed specifically for this problem.
5. Most times, you'll want to run through multiple repetions of the annealing runs. It is helpful to see, for example, how similar the states between 20 different runs. If the same or very similar state is acheived 20 times, it's likely that you've adequeately converged on a nearly-optimal answer.


