import numpy as np
import random
import sys
sys.setrecursionlimit(100000)  # to temporarily solve Recursion Depth Limit issue

# Reference :
# https://www.reddit.com/r/learnmachinelearning/comments/fmx3kv/empirical_example_of_mcts_calculation_puct_formula/

# PUCT formula : https://colab.research.google.com/drive/14v45o1xbfrBz0sG3mHbqFtYz_IrQHLTg#scrollTo=1VeRCpCSaHe3

# https://en.wikipedia.org/wiki/Monte_Carlo_tree_search#Exploration_and_exploitation
cfg_puct = np.sqrt(2)  # to balance between exploitation and exploration
puct_array = []  # stores puct ratio for every child nodes for argmax()


# determined by PUCT formula
def find_best_path(parent):
    if (parent == root) | (len(parent.nodes) == 0):
        return parent

    for N in parent.nodes:
        puct_array.append(N.puct)

    max_index = np.argmax(puct_array)
    puct_array.clear()  # resets the list so that other paths could reuse it

    #  leaf node has 0 child node
    is_leaf_node = (len(parent.nodes[max_index].nodes) == 0)
    if is_leaf_node:
        return parent.nodes[max_index]

    return parent.nodes[max_index]


class Mcts:
    def __init__(self, parent):
        # https://www.tutorialspoint.com/python_data_structure/python_tree_traversal_algorithms.htm
        # https://www.geeksforgeeks.org/sum-parent-nodes-child-node-x/

        self.parent = parent  # this is the parent node
        self.nodes = []  # creates an empty list with no child nodes initially
        self.data = 0  # can be of any value, but just initialized to 0
        self.visit = 1  # when a node is first created, it is counted as visited once
        self.win = 0  # because no play/simulation had been performed yet
        self.loss = 0  # because no play/simulation had been performed yet
        self.puct = 0  # initialized to 0 because game had not started yet

    # this function computes W/N ratio for each node
    def compute_total_win_and_visits(self, total_win=0, visits=0):
        if self.win:
            total_win = total_win + 1

        if self.visit:
            visits = visits + 1

        if self.nodes:  # if there is/are child node(s)
            for n in self.nodes:  # traverse down the entire branch for each child node
                n.compute_total_win_and_visits(total_win, visits)

        return total_win, visits  # same order (W/N) as in
        # https://i.imgur.com/uI7NRcT.png inside each node

    # Selection stage of MCTS
    def select(self):
        # traverse recursively all the way down from the root node
        # to find the path with the highest W/N ratio (this ratio is determined using PUCT formula)
        # and then select that leaf node to do the new child nodes insertion
        leaf = find_best_path(self)  # returns a reference pointer to the desired leaf node
        leaf.insert()  # this leaf node is selected to insert child nodes under it

    # Expansion stage of MCTS
    # Insert Child Nodes for a leaf node
    def insert(self):
        num_of_possible_game_states = 8  # assuming that we are playing tic-tac toe

        for S in range(num_of_possible_game_states):
            self.nodes.append(Mcts(self))  # inserts child nodes

        self.nodes[len(self.nodes) - 1].simulate()

    # Simulation stage of MCTS
    def simulate(self):
        # will replace the simulation stage with a neural network in the future
        self.win = random.randint(0, 1)  # just for testing purpose, so it is either win (1) or lose (0)
        self.loss = ~self.win & random.randint(0, 1)  # 'and' with randn() for tie/draw situation
        self.backpropagation(self.win, self.loss)

    # Backpropagation stage of MCTS
    def backpropagation(self, win, loss):
        # traverses upwards to the root node
        # and updates PUCT ratio for each parent nodes
        # computes the PUCT expression Q+U https://slides.com/crem/lc0#/9

        if self.parent == 0:
            num_of_parent_visits = 0
        else:
            num_of_parent_visits = self.parent.visit

        total_win_for_all_child_nodes, num_of_child_visits = self.compute_total_win_and_visits(0, 0)

        self.visit = num_of_child_visits

        # traverses downwards all branches (only for those branches involved in previous play/simulation)
        # and updates PUCT values for all their child nodes
        self.puct = (total_win_for_all_child_nodes / num_of_child_visits) + \
            cfg_puct * np.sqrt(num_of_parent_visits) / (num_of_child_visits + 1)

        if self.parent == root:  # already reached root node
            self.select()

        else:
            self.parent.visit = self.parent.visit + 1
            if win:
                if self.parent.parent:  # grandparent node (same-coloured player) exists
                    self.parent.parent.win = self.parent.parent.win + 1

            if (win == 0) & (loss == 0):  # tie is between loss (0) and win (1)
                self.parent.win = self.parent.win + 0.5  # parent node (opponent player)

                if self.parent.parent:  # grandparent node (same-coloured player) exists
                    self.parent.parent.win = self.parent.parent.win + 0.5

            self.parent.backpropagation(win, loss)

    # Print the Tree
    def print_tree(self, child):
        for x in child.nodes:
            print(x.data)
            if x.nodes:
                self.print_tree(x.nodes)


root = Mcts(0)  # we use parent=0 because this is the head/root node
root.select()
print(root.print_tree(root))