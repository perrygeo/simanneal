import random
import sys
import time

from helper import distance, cities, distance_matrix
from simanneal import Annealer

if sys.version_info.major >= 3:  # pragma: no cover
    from io import StringIO
else:
    from StringIO import StringIO


class TravellingSalesmanProblem(Annealer):
    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, distance_matrix, initial_state=None, load_state=None):
        self.distance_matrix = distance_matrix
        super(TravellingSalesmanProblem, self).__init__(
            initial_state=initial_state, load_state=load_state)

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

    tsp = TravellingSalesmanProblem(distance_matrix, initial_state=init_state)

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

    tsp = TravellingSalesmanProblem(distance_matrix, initial_state=init_state)

    # since our state is just a list, slice is the fastest way to copy
    tsp.copy_strategy = "slice"

    auto_schedule = tsp.auto(minutes=0.05)
    tsp.set_schedule(auto_schedule)

    assert tsp.Tmax == auto_schedule['tmax']
    assert tsp.Tmin == auto_schedule['tmin']
    assert tsp.steps == auto_schedule['steps']
    assert tsp.updates == auto_schedule['updates']


def test_save_load_state(tmpdir):
    # initial state, a randomly-ordered itinerary
    init_state = list(cities.keys())
    random.shuffle(init_state)

    tsp = TravellingSalesmanProblem(distance_matrix, initial_state=init_state)
    tsp.copy_strategy = "slice"

    statefile = str(tmpdir.join("state.pickle"))
    tsp.save_state(fname=statefile)

    init_state2 = init_state[1:] + init_state[:1]

    tsp2 = TravellingSalesmanProblem(distance_matrix,
                                     initial_state=init_state2)
    tsp2.load_state(fname=statefile)
    assert tsp.state == tsp2.state


def test_load_state_init(tmpdir):
    # initial state, a randomly-ordered itinerary
    init_state = list(cities.keys())
    random.shuffle(init_state)

    tsp = TravellingSalesmanProblem(distance_matrix, initial_state=init_state)
    tsp.copy_strategy = "slice"

    statefile = str(tmpdir.join("state.pickle"))
    tsp.save_state(fname=statefile)

    tsp2 = TravellingSalesmanProblem(distance_matrix, load_state=statefile)
    assert tsp.state == tsp2.state


def test_default_update_formatting():
    init_state = list(cities.keys())
    tsp = TravellingSalesmanProblem(distance_matrix, initial_state=init_state)

    # fix the start time and patch time.time() to give predictable Elapsed and Remaining times
    tsp.start = 1.0
    time.time = lambda: 9.0

    # for step=0, the output should be column headers followed by partial data
    sys.stderr = StringIO()
    tsp.default_update(0, 1, 2, 3, 4)
    output = sys.stderr.getvalue().split('\n')
    assert 3 == len(output)
    assert   ' Temperature        Energy    Accept   Improve     Elapsed   Remaining' == output[1]
    assert '\r     1.00000          2.00                         0:00:08            ' == output[2]

    # when step>0, default_update should use \r to overwrite the previous data
    sys.stderr = StringIO()
    tsp.default_update(10, 1, 2, 3, 4)
    output = sys.stderr.getvalue().split('\n')
    assert 1 == len(output)
    assert '\r     1.00000          2.00   300.00%   400.00%     0:00:08    11:06:32' == output[0]
