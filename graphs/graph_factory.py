''' A factory class to help with the creation of objects
of the different types of graph types. I added this to make it
easier for future development. It is not really need for the
three graph implementations we have right now. '''

import enum
import random
import string
import time
from random import randint

from graphs.complete_graph import CompleteGraph
from graphs.graph import Graph
from graphs.hub_and_spoke_graph import HubAndSpoke
from nodeAndRepairNode.nodes import Node


class GraphTypes(enum.Enum):
    ''' Defines an enum to avoid using strings directly and
    add more type checking '''

    complete = 1
    hub_and_spoke = 2
    generic = 3


class GraphFactory(object):
    ''' This the base class for the factories. '''

    def __init__(self, graph_type, num_of_nodes=0):

        # type check
        if not isinstance(graph_type, GraphTypes):
            raise Exception("Use the GraphTypes enum as a param")
        else:
            self.graph_type = graph_type

        self.num_of_nodes = num_of_nodes

    def get_graph(self):
        ''' sub classes must implement this method '''
        raise NotImplementedError


class GraphFactoryNoData(GraphFactory):
    ''' A graph  factory that doesn't add any data. It wil generate graphs
    with empty nodes or empty node lists. You probably want to use the other implementations
    since they can also add randomized data and take # of nodes as an argument '''

    def __init__(self, graph_type, num_of_nodes=0):
        super().__init__(graph_type, num_of_nodes)

    def get_graph(self):
        ''' Creates graphs of different type based on the parameter '''

        if self.graph_type.value == 1:
            graph = CompleteGraph()

        elif self.graph_type.value == 2:
            graph = HubAndSpoke(Node(""))
            self.num_of_nodes-=1

        else:
            graph = Graph()

        # create the nodes
        for _ in range(self.num_of_nodes):
            graph.add_node(Node(""))

        return graph


class GraphFactoryAlphaNumeric(GraphFactory):
    ''' Implementation of the the factory class that populates the
    graph with alpahnumeric values. Pass a random seed other than -1
    to set the seed.

    .. note:: it doesn't create any edges b/n the nodes. Call rand edge
            from graph if you would like to randomly create the edges.
    '''

    def __init__(self, graph_type, num_of_nodes, random_seed=-1):

        # set random seed if not -1
        if random_seed != -1:
            random.seed(random_seed)

        self.seed = random_seed

        super().__init__(graph_type, num_of_nodes)

    def get_random_alpha_numeric(self, upper_num=1000, lower_num=0):
        ''' returns a string with a randomized, not necessarily unique,
        value containing numbers and characters '''

        # randomize on each generation
        if self.seed != -1:
            random.seed(time.time())

        number = randint(lower_num, upper_num)

        # get five letters
        letter = "".join(random.choice(string.ascii_letters) for n in range(5))

        return str(number) + letter

    def get_graph(self):
        ''' implementation of the factory '''

        graph = None
        # create a graph object
        if self.graph_type.value == 1:
            graph = CompleteGraph()

        elif self.graph_type.value == 2:
            graph = HubAndSpoke(Node(self.get_random_alpha_numeric()))
            self.num_of_nodes-=1

        else:
            graph = Graph()


        # create the nodes
        for _ in range(self.num_of_nodes):
            # get value for node
            node_value = self.get_random_alpha_numeric()
            graph.add_node(Node(node_value))

        # shuffle the nodes
        random.shuffle(graph.list_nodes)

        return graph