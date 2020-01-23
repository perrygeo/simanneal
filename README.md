# Python module for simulated annealing

[![Build Status](https://travis-ci.org/perrygeo/simanneal.svg?branch=master)](https://travis-ci.org/perrygeo/simanneal)
[![PyPI version](https://badge.fury.io/py/simanneal.svg)](https://badge.fury.io/py/simanneal)

This module performs [simulated annealing optimization](http://en.wikipedia.org/wiki/Simulated_annealing) to find the optimal state of a system. It is inspired by the metallurgic process of annealing whereby metals must be cooled at a regular schedule in order to settle into their lowest energy state. 

Simulated annealing is used to find a close-to-optimal solution among an extremely large (but finite) set of potential solutions. It is particularly useful for [combinatorial optimization](http://en.wikipedia.org/wiki/Combinatorial_optimization) problems defined by complex objective functions that rely on external data. 

The process involves:

1. Randomly **move** or alter the **state** 
2. Assess the **energy** of the new state using an objective function
3. Compare the energy to the previous state and 
   decide whether to accept the new solution or
   reject it based on the current **temperature**.
4. Repeat until you have converged on an acceptable answer


For a move to be accepted, it must meet one of two requirements:

* The move causes a decrease in state energy (i.e. an improvement in the objective function)
* The move increases the state energy (i.e. a slightly worse solution) but is within the bounds of the temperature. The temperature exponetially decreases as the algorithm progresses. In this way, we avoid getting trapped by local minima early in the process but start to hone in on a viable solution by the end. 


## Example: Travelling Salesman Problem

The quintessential discrete optimization problem is the [travelling salesman problem](http://en.wikipedia.org/wiki/Travelling_salesman_problem). 

> Given a list of locations, what is the shortest possible route 
> that hits each location and returns to the starting city?

To put it in terms of our simulated annealing framework:
* The **state** is an ordered list of locations to visit
* The **move** shuffles two cities in the list
* The **energy** of a give state is the distance travelled

## Quickstart

Install it first
```bash
pip install simanneal  # from pypi

pip install -e git+https://github.com/perrygeo/simanneal.git  # latest from github
```

To define our problem, we create a class that inherits from `simanneal.Annealer`

```python
from simanneal import Annealer
class TravellingSalesmanProblem(Annealer):
    """Test annealer with a travelling salesman problem."""
```

Within that class, we define two required methods. First, we define the move:

```python
    def move(self):
        """Swaps two cities in the route."""
        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]
```

Then we define how energy is computed (also known as the *objective function*):
```python
    def energy(self):
        """Calculates the length of the route."""
        e = 0
        for i in range(len(self.state)):
            e += self.distance(cities[self.state[i - 1]],
                          cities[self.state[i]])
        return e
```

Note that both of these methods have access to `self.state` which tracks the current state of the process. 

So with our problem specified, we can construct a ` TravellingSalesmanProblem` instance and provide it a starting state

```python
initial_state = ['New York', 'Los Angeles', 'Boston', 'Houston']
tsp = TravellingSalesmanProblem(initial_state)
```

And run it
```python
itinerary, miles = tsp.anneal()
```

See [examples/salesman.py](https://github.com/perrygeo/simanneal/blob/master/examples/salesman.py) to see the complete implementation.

## Annealing parameters

Getting the annealing algorithm to work effectively and quickly is a matter of tuning parameters. The defaults are:
```python
Tmax = 25000.0  # Max (starting) temperature
Tmin = 2.5      # Min (ending) temperature
steps = 50000   # Number of iterations
updates = 100   # Number of updates (by default an update prints to stdout)
```
These can vary greatly depending on your objective function and solution space.

 A good rule of thumb is that your initial temperature `Tmax` should be set to accept roughly 98% of the moves and that the final temperature `Tmin` should be low enough that the solution does not improve much, if at all. 

The number of `steps` can influence the results; if there are not enough iterations to adequately explore the search space it can get trapped at a local minimum. 

The number of updates doesn't affect the results but can be useful for examining the progress. The default update method (`Annealer.update`) prints a table to stdout and includes the current temperature, state energy, the percentage of moves accepted and improved and elapsed and remaining time. You can override `.update` and provide your own custom reporting mechanism to e.g. graphically plot the progress.

If you want to specify them manually, the are just attributes of the `Annealer` instance. 
```python
tsp.Tmax = 12000.0
...
```
However, you can use the `.auto` method which attempts to explore the search space to determine some decent starting values and assess how long each iteration takes. This allows you to specify roughly how long you're willing to wait for results.

```python
auto_schedule = tsp.auto(minutes=1) 
# {'tmin': ..., 'tmax': ..., 'steps': ...}

tsp.set_schedule(auto_schedule)
itinerary, miles = tsp.anneal()
```

## Extra data dependencies

You might have noticed that the `energy` function above requires a `cities` dict 
that is presumably defined in the enclosing scope. This is not necessarily a good
design pattern. The dependency on additional data can be made explicit by passing 
them into the constructor like so

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, distance_matrix):
        self.distance_matrix = distance_matrix
        super(TravellingSalesmanProblem, self).__init__(state)  # important!

The last line (calling init on the super class) is critical. 

## Optimizations

For some problems the `energy` function is prohibitively expensive to calculate
after every move. It is often possible to compute the change in energy that a
move causes much more efficiently. A delta value can be returned from `move` to
update the energy value without calling `energy` multiple times.

## Implementation Details

The simulated annealing algorithm requires that we track state (current, previous, best) and thus means we need to copy the `self.state` frequently.

Copying an object in Python is not always straightforward or performant. The standard library provides a `copy.deepcopy()` method to copy arbitrary python objects but it is very expensive. Certain objects can be copied by more efficient means: lists can be sliced and dictionaries can use their own .copy method, etc.

In order to facilitate flexibility, you can specify the `copy_strategy` attribute
which defines one of:
* `deepcopy`: uses `copy.deepcopy(object)`
* `slice`: uses `object[:]`
* `method`: uses `object.copy()`

If you want to implement your own custom copy mechanism, you can override the `copy_state` method.

## Notes

1. Thanks to Richard J. Wagner at University of Michigan for writing and contributing the bulk of this code.
2. Some effort has been made to increase performance but this is nowhere near as fast as optimized solutions written in other low-level languages. On the other hand, this is a very flexible, Python-based solution that can be used for rapidly 
experimenting with a computational problem with minimal overhead. 
3. Using PyPy instead of CPython can yield substantial increases in performance.
4. For certain problems, there are simulated annealing techniques that are highly customized and optimized for the particular domain
    * For conservation planning, check out [Marxan](http://www.uq.edu.au/marxan/) which is designed to prioritize conservation resources according to multiple planning objectives
    * For forest management and timber harvest scheduling, check out [Harvest Scheduler](https://github.com/Ecotrust/harvest-scheduler) which optimizes forestry operations over space and time to meet multiple objectives. 
5. Most times, you'll want to run through multiple repetions of the annealing runs. It is helpful to examine the states between 20 different runs. If the same or very similar state is acheived 20 times, it's likely that you've adequeately converged on a nearly-optimal answer.


