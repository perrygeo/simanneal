import math
import random

from helper import distance, cities, distance_matrix
from simanneal import Annealer


class TravellingSalesmanProblem(Annealer):
    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, distance_matrix):
        self.distance_matrix = distance_matrix
        super(TravellingSalesmanProblem, self).__init__(state)  # important!

    def move(self):
        """Swaps two cities in the route."""
        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """Calculates the length of the route."""
        e = 0
        for i in range(len(self.state)):
            e += self.distance_matrix[self.state[i - 1]][self.state[i]]
        return e


def test_tsp_example():
    # initial state, a randomly-ordered itinerary
    init_state = list(cities.keys())
    random.shuffle(init_state)

    tsp = TravellingSalesmanProblem(init_state, distance_matrix)

    # since our state is just a list, slice is the fastest way to copy
    tsp.copy_strategy = "slice"
    tsp.steps = 50000

    state, e = tsp.anneal()
    while state[0] != 'New York City':
        state = state[1:] + state[:1]  # rotate NYC to start

    assert len(state) == len(cities)


def test_auto():
    # initial state, a randomly-ordered itinerary
    init_state = list(cities.keys())
    random.shuffle(init_state)

    tsp = TravellingSalesmanProblem(init_state, distance_matrix)

    # since our state is just a list, slice is the fastest way to copy
    tsp.copy_strategy = "slice"

    auto_schedule = tsp.auto(minutes=0.05) 
    tsp.set_schedule(auto_schedule)

    assert tsp.Tmax == auto_schedule['tmax']
    assert tsp.Tmin == auto_schedule['tmin']
    assert tsp.steps == auto_schedule['steps']
    assert tsp.updates == auto_schedule['updates']


def test_state(tmpdir):
    # initial state, a randomly-ordered itinerary
    init_state = list(cities.keys())
    random.shuffle(init_state)

    tsp = TravellingSalesmanProblem(init_state, distance_matrix)
    tsp.copy_strategy = "slice"

    statefile = str(tmpdir.join("state.pickle"))
    tsp.save_state(fname=statefile)

    tsp2 = TravellingSalesmanProblem(init_state, distance_matrix)
    tsp2.load_state(fname=statefile)
    assert tsp.state == tsp2.state
    
