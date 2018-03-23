import random
import uuid


class Graph(object):

    # TODO: Graph needs it's own unique ID, it will inject to every node as it gets added
    # then stable sort by each graph uuid, then sort by each node uuid so nodes in the same graph will be closer,
    # needed for compression algorithm

    # TODO: rather than checking if everything in in list_nodes, check n.graph_id == self.graph_id
    # this doesn't actually show if node is CURRENTLY in graph though,
    # as it could have been deleted and still have the same uid

    def __init__(self, n_list=None):

        self.list_nodes = []
        self.graph_id = uuid.uuid4()

        # add the nodes passed in
        if n_list:
            for node in n_list:
                self.add_node(node)

    def add_edge(self, n1, n2):
        """
        n1 must be/will be a node in the graph (1st param), if it isn't, it's added to the graph
        n2 can be in graph, doesn't have to be (add_node not called)
        n2 is added to n1's adj list by calling Node.add_edge()
        Needs to be redefined by other graphs to check for duplicates,
        add additional rules for new graph implementations
        """
        if n1.graph_id != self.graph_id:  # check if n1 not in graph
            self.add_node(n1)
        n1.add_edge(n2)  # n2 is added to n1's list, directed graph, n2 doesn't add n1

    def delete_edge(self, n1, n2):
        """
        n2 is removed from n1's adj list by calling Node.delete_edge()
        One node must be in graph, the other doesn't have to be (so can remove edges between graphs)
        """
        if n1.graph_id == self.graph_id or n2.graph_id == self.graph_id:  # if either in graph, try deleting
            n1.delete_edge(n2)  # List.remove() throws ValueError if remove non existing
            # n2.delete_edge(n1) our's is a directed graph, must call delete_edge 2x if want no connections at all

    def delete_node(self, n):
        """removes the node from the graph,
        clears the adj list therein,
        resets the node.graph_id = None,
        DOES NOT remove external references to the node"""
        # TODO: remove external references to the node? See complete graph
        if n.graph_id == self.graph_id:
            # the node and it's list of edges is deleted
            self.list_nodes.remove(n)  # delete the node, error if nonexistent
            n.graph_id = None  # reset uid to reflect outside the graph
            for x in n.edges:  # clear the adj list
                self.delete_edge(x, n)
        else:
            raise ValueError('Node not in graph, cannot delete node')

    def add_node(self, n):
        """
        Adds a node to the Graph data structures, but it won't be connected by any edge.
        Duplicate nodes fail silently.
        New implementations should redefine this function.
        """
        if n not in self.list_nodes:  # prevent from adding >1x
            n.graph_id = self.graph_id
            self.list_nodes.append(n)

    def __str__(self):
        """ Prints out graphs in a nice format """
        formatted = " "

        for node in self.list_nodes:
            formatted += str(node) + "\n"
            for adj_node in node.edges:
                formatted += "\t" + str(adj_node) + "\n"

        return formatted

    def __eq__(self, other):
        """ compares two graphs for equality

        @warning can be very slow. Don't compare two graphs unless in a test setting

        Two graphs are considered equal iff they have the same exact nodes, in the same
        exactly positions. The ordering of nodes makes a difference to our algorithms
        so graphs w/ the same nodes in different positions within the lists
        should be considered different. """

        # type check
        if not isinstance(other, Graph):
            return False

        # check for number of nodes
        if len(self.list_nodes) != len(other.list_nodes):
            return False

        for node_index, node1 in enumerate(self.list_nodes):

            node2 = other.list_nodes[node_index]

            # check ids of "parent nodes"
            if node1.uid != node2.uid:
                return False

            # check ids of out going nodes
            for edge_index, edge1 in enumerate(node1.edges):
                edge2 = node2.edges[edge_index]

                if edge1.uid != edge2.uid:
                    return False

        # they must be equal
        return True


class Cluster(Graph):
    # apparently we're not using this class anymore...
    # ONLY one cluster at a time in our system (otherwise more uid's)
    def add_graph(self, g):
        """
        Takes a random node from both graphs and calls addEdge, returns the list of nodes
        """
        node1 = random.choice(self.list_nodes)
        node2 = random.choice(g.list_nodes)
        self.add_edge(node1, node2)

    def add_graph_by_node(self, n):
        """
        Like add_graph, but allows specification of one of the nodes (the param node).
        Randomly selects one internal node, calls add_edge on the param node,
        which doesn't have to be in the cluster/graph (param node could be external)
        """
        rand_node = random.choice(self.list_nodes)
        self.add_edge(n, rand_node)


"""
These graphs will consist exclusively of nodes which
are connected to every other node in the graph
"""


class CompleteGraph(Graph):
    list_nodes = []

    def __init__(self, n_list=None):  # n_list = None allows us to optionally pass all the nodes we want at start
        if n_list:
            Graph.__init__(n_list)  # this is a placeholder
            # connect all nodes in n_list here
            # may need to redesign functions or add new functions here.
            # Maybe a hub and spoke function called recursively?
        Graph.__init__(self, n_list)

    def add_edge(self, n1, n2):
        if n1 not in self.list_nodes or n2 not in self.list_nodes:
            self.add_node(n1)
            self.add_node(n2)
        if n1 not in n2.edges:
            n1.add_edge(n2)  # directed graph

    def delete_edge(self, n1, n2):
        if n1 in self.list_nodes and n2 in self.list_nodes:  # if edge inside graph and not out into cluster
            raise ValueError('Edge removal violates complete graph structure')
            # TODO: maybe this should be a warning, not an error, so it doesn't stop the program?
        else:
            n1.delete_edge(n2)  # directed graph

    def delete_node(self, n):
        """removes the node from the graph,
        clears the adj list therein,
        and removes all references other nodes hold to the deleted node"""
        if n in self.list_nodes:
            # the node and it's list of edges is deleted
            self.list_nodes.remove(n)
            for x in n.edges:
                self.delete_edge(x, n)
            # every outside reference to the node is deleted - costly
            for x in self.list_nodes:  # for all other nodes
                while self.list_nodes[x].edges.count(n) != 0:  # remove n as many times as it appears in edges
                    self.list_nodes[x].edges.remove(n)
        else:
            raise ValueError('Node not in graph')

    def add_node(self, n):  # TODO: Simonne check this
        if n not in self.list_nodes:
            self.list_nodes.append(n)
            for i in range(len(self.list_nodes)):
                self.list_nodes[i].add_edge(n)
        else:
            raise ValueError('Node already in graph')

    """
    Since every node ends up being connected to every other node
    anyway, this method is effectively the same as add_node
    """
    # def add_node_rand(self, n):
    #
    #     return 0


"""
These graphs will consist of many nodes all connected
only to one central hub node.
This graph should implement from the top down a guaranteed connected graph 
rather than the Graph class' possible bottom-up of creation of a connected graph
"""


class HubAndSpokeGraph(Graph):
    list_nodes = []

    def __init__(self, hub, n_list=None):
        Graph.__init__(self, n_list)
        self.hub_node = hub

    def add_edge(self, n1, n2):
        if self.hub_node not in (n1, n2):
            raise ValueError('Hub node not targeted')  # wouldn't it be easier to change the parameters?
            # Or overriding, so can't? IDK.  Is it necessary to override/can we create a new function?
        else:
            if n2 not in n1.edges:  # TODO: fix other classes so they look like this
                n1.add_edge(n2)  # n2 is appended to n1's list

    def delete_edge(self, n1, n2):
        if n1 in n2.edges:
            n1.delete_edge(n2)
        else:
            raise ValueError('Edge does not exist')  # TODO: should exit quietly instead?

    def delete_node(self, n):
        if n in self.list_nodes:
            # TODO: call delete_edge remove n from nodes that list it in otherNode.edge
            # see general Graph class above
            self.list_nodes.remove(n)
            for i in range(len(self.list_nodes)):
                self.list_nodes[i].delete_edge(n)
        else:
            raise ValueError('Node does not exist, cannot be deleted')

    def add_node(self, n):
        if n not in self.list_nodes:
            self.list_nodes.append(n)
            n.add_edge(self.hub_node)
        else:
            raise ValueError('Node already exists in graph')
            # TODO: exit/fail quietly w/out error b/c called by other functions

    """
    Not necessary since an add is not allowed unless the hub is
    targeted; adding a random node is effectively no different
    than adding a particular node
    """
    # def add_node_rand(self, n):
    #
