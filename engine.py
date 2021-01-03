from utils import (start_position, 
                   list_moves,
                   update_position,
                   create_view,
                   print_position,
                   find_piece)
from collections import namedtuple
from tqdm import tqdm
from time import time

# if it is my turn, a node is represented by a namedtuple
# "view": the current view of the board
# "possible": the list of possible positions
# "turn": True

# if it is the opponents turn, a node is represented by a namedtuple
# "view": None
# "possible": the list of possible positions AFTER my last move,BEFORE getting the new view
# "turn": False
Node = namedtuple("Node", ["view", "possible", "turn"])


# here we will store the positions for wich we already know the score at some depths
lookup_table = {}
TableEntry = namedtuple("TableEntry", ["value", "principal_variation", "depth", "flag"])


def update_possible(possible, after_move, view):
    new_possible = set()
    if after_move:
        for position in possible:
            moves = list_moves(position, False)
            for move in moves:
                new_position = update_position(position, move, False)
                new_view = create_view(new_position)
                if view == new_view:
                    new_possible.add(new_position)
    else:
        for position in possible:
            new_view = create_view(position)
            if view == new_view:
                new_possible.add(position)
    return frozenset(new_possible)


def update_node_1(node, move):
    possible = set()
    for position in node.possible:
        new_position = update_position(position, move, True)
        possible.add(new_position)
    child = Node(view=None,
                 possible=frozenset(possible),
                 turn=not node.turn)
    return child


def update_node_2(node, view, possible):
    possible = update_possible(possible, True, view)
    child = Node(view=view,
                 possible=possible,
                 turn=not node.turn)
    return child


def is_terminal(node): 
    total = 0
    position = next(iter(node.possible))
    total += len(find_piece(position, "K"))
    total -= len(find_piece(position, "k"))
    return total


def position_evaluation(position):
    if len(find_piece(position, "K")) == 0:
        return -2000
    if len(find_piece(position, "k")) == 0:
        return 2000
    total = 0
    total += len(find_piece(position, "N"))
    total -= len(find_piece(position, "n"))
    return total


def simple_static_evaluation(node):
    position = next(iter(node.possible))
    return position_evaluation(position)


class additivetuple(tuple):
    def __add__(self, other):
        return additivetuple(i+j for i,j in zip(self, other))
    def __neg__(self):
        return additivetuple(-i for i in self)
    def __mul__(self, n):
        return additivetuple(i*n for i in self)
    def __rmul__(self, n):
        return additivetuple(n*i for i in self)


def static_evaluation(node):
    position = next(iter(node.possible))
    if len(find_piece(position, "K")) == 0:
        win_lose_score = -2000
    elif len(find_piece(position, "k")) == 0:
        win_lose_score = 2000
    else:
        win_lose_score = 0

    my_knights = len(find_piece(position, "N"))
    opponent_knights = len(find_piece(position, "n"))
    material_score = my_knights - opponent_knights

    # visibility score
    if node.turn:
        my_visibility_score = -len(find_piece(node.view, "#"))
        opponent_visibility_scores = []
        for position in node.possible:
            opponent_view = create_view(position, False)
            opponent_visibility_scores.append(-len(find_piece(node.view, "#")))
        opponent_visibility_score = sum(opponent_visibility_scores)/len(opponent_visibility_scores)
    else:
        my_visibility_scores = []
        opponent_visibility_scores = []
        for position in node.possible:
            my_view = create_view(position, True)
            my_visibility_scores.append(-len(find_piece(my_view, "#")))

            opponent_view = create_view(position, False)
            opponent_visibility_scores.append(-len(find_piece(opponent_view, "#")))

        my_visibility_score = sum(my_visibility_scores)/len(my_visibility_scores)
        opponent_visibility_score = sum(opponent_visibility_scores)/len(opponent_visibility_scores)

    visibility_score = my_visibility_score - opponent_visibility_score

    return additivetuple((win_lose_score, material_score, visibility_score))


def children_generator(node):
    if node.turn:
        moves = list_moves(node.view)
        for move in moves:
            yield update_node_1(node, move), move
    else:
        for position in node.possible:
            view = create_view(position)
            new_possible = update_possible(node.possible, False, view)
            moves = list_moves(position, False)
            for move in moves:
                yield update_node_2(node, create_view(update_position(position, move, False)), new_possible), move


def minimax(node, depth):
    value, principal_variation = negamax(node, depth, -additivetuple([float("inf")]*3), additivetuple([float("inf")]*3))
    lookup_table["principal_variation"] = principal_variation
    if node.turn:
        return value, principal_variation
    else:
        return -value, principal_variation


def negamax(node, depth, alpha, beta):
    alpha_orig = alpha

    # first check if the score is already known
    if node in lookup_table:
        entry = lookup_table[node]
        if entry.depth >= depth:
            if entry.flag == 0:
                return entry.value, entry.principal_variation
            elif entry.flag == -1:
                alpha = max(alpha, entry.value)
            else:
                beta = min(beta, entry.value)

            if alpha >= beta:
                return entry.value, entry.principal_variation

    # base case for the recursion
    if depth == 0 or is_terminal(node) != 0:
        if node.turn:
            sign = 1
        else:
            sign = -1
        value = sign*static_evaluation(node)
        return value, []

    # recursion
    value = -additivetuple([float("inf")]*3)
    children = children_generator(node)
    for child, move in children:
        child_value, principal_variation = negamax(child, depth-1, -beta, -alpha)
        child_value = -child_value
        if child_value[0] > 1000:
            child_value = additivetuple((child_value[0] - 1, *child_value[1:]))
        if child_value > value:
            value = child_value
            best_move = move
            best_principal_variation = principal_variation
        alpha = max(alpha, value)
        if alpha >= beta:
            break

    principal_variation = [best_move] + best_principal_variation
    if value <= alpha_orig:
        new_entry = TableEntry(value=value,
                               principal_variation=principal_variation,
                               depth=depth,
                               flag=1)
    elif value >= beta:
        new_entry = TableEntry(value=value,
                               principal_variation=principal_variation,
                               depth=depth,
                               flag=-1)
    else:
        new_entry = TableEntry(value=value,
                               principal_variation=principal_variation,
                               depth=depth,
                               flag=0)
    lookup_table[node] = new_entry

    return value, principal_variation


def iterative_deepening(node, max_depth=float("inf")):
    depth = 0
    t0 = time()
    while depth <= max_depth:
        score, principal_variation = minimax(node, depth)
        print("score", score, "at depth", depth, "in", time()-t0, "seconds")
        depth += 1


if __name__ == "__main__":

    # simple test
    node = Node(possible=frozenset({start}),
                view=create_view(start),
                turn=True)
    iterative_deepening(node, 5)